import datetime
from bs4 import BeautifulSoup
from philip_snat_models.khl import urls
from philip_snat_models.khl.utils._request import req
from philip_snat_models.khl.const import (
    clr,
    team_names_map,
    team_sportbox_russian_name_map,
    team_stats_column_map,
    today,
)
import philip_snat_models.khl.utils.utils as utils
from app.models.philip_snat_khl_game import PhilipSnatKhlGame


class Getter:
    def __init__(self, logger, db):
        self.logger = logger
        self.db = db
        self.team_stats_quant = None
        self.download_stats_quant()

    def download_stats_quant(self):
        response = req(urls.TEAM_STATS_QUANT)
        if response:
            self.team_stats_quant = response
            self.logger.log(3, "Team stats downloaded successfully", color=clr.GREEN)
        else:
            self.logger.log_error(3, "Failed to download team stats")

    def get_team_stats_quant_html(self, team_name):
        if not self.team_stats_quant:
            self.logger.log_error(1, "No team stats available.")
            return None

        team_name = team_names_map[team_name]["quant"]

        try:
            soup = BeautifulSoup(self.team_stats_quant.text, "html.parser")
            table = soup.find("table", id="statistics")
            if not table:
                self.logger.log_error(1, "Table with id='statistics' not found")
                return None

            rows = table.find_all("tr")
            for row in rows:
                th_elements = row.find_all("th")
                if len(th_elements) > 1:
                    if team_name.lower() in th_elements[1].get_text().lower():
                        return row

            self.logger.log_error(1, f"Team '{team_name}' not found in stats")
            return None
        except Exception as e:
            self.logger.log_error(1, f"Error parsing team stats: {str(e)}")
            return None

    def get_team_stats_quant(self, team_name):
        html = self.get_team_stats_quant_html(team_name)
        if html is None:
            return None

        td_elements = html.find_all("td")
        th_elements = html.find_all("th")
        result = {"rank": th_elements[0].get_text().strip()}

        for stat_name, column_index in team_stats_column_map.items():
            result[stat_name] = td_elements[column_index].get_text().strip()

        return result

    def get_team_last_5_games(self, team_name):
        self.logger.log(2, f"\t Getting {team_name} last 5 games", color=clr.ORANGE)

        html = req(
            team_names_map[team_name]["url_template"].replace(
                "__URL_NAME__", team_names_map[team_name]["sportbox_url_name"]
            )
        )
        if not html:
            self.logger.log_error(3, "Failed to download team last games")
            return None

        soup = BeautifulSoup(html.text, "html.parser")
        div = soup.find("div", attrs={"class": "_Sportbox_Spb2015_Components_TableGames_TableGames"})
        a_elements = div.find_all("a")[5:10]

        games = []
        for i, a_element in enumerate(a_elements):
            if i >= 5:
                break
            home_team_box = a_element.find("div", attrs={"class": "box-left"})
            home_team = home_team_box.find("div", attrs={"class": "name"}).get_text().strip()

            away_team_box = a_element.find("div", attrs={"class": "box-right"})
            away_team = away_team_box.find("div", attrs={"class": "name"}).get_text().strip()

            score_box = a_element.find("div", attrs={"class": "box-center"})
            score = score_box.find("span", attrs={"class": "score"}).get_text().strip()
            result = score.split(":")
            home_score, away_score = result[0], result[1]

            OT = False
            SO = False
            comment = a_element.find("div", attrs={"class": "comment"})
            if comment:
                OT = True
                if "б" in comment.get_text():
                    SO = True

            if home_team == "Динамо":
                img = home_team_box.find("img")["src"]
                home_team = "Динамо Москва" if "ru" in img else "Динамо Минск"
            if away_team == "Динамо":
                img = home_team_box.find("img")["src"]
                away_team = "Динамо Москва" if "ru" in img else "Динамо Минск"

            played_as = "home" if team_names_map[team_name]["sportbox"] == home_team else "away"
            home_team = team_sportbox_russian_name_map[home_team]
            away_team = team_sportbox_russian_name_map[away_team]

            winner = "home" if int(home_score) > int(away_score) else "away"
            total_goals_no_ot = int(home_score) + int(away_score)
            opponent_team = away_team if played_as == "home" else home_team
            opponent_rank = self.get_team_stats_quant(opponent_team)["rank"]

            games.append({
                "home_team": home_team,
                "away_team": away_team,
                "home_score": home_score,
                "away_score": away_score,
                "winner": winner,
                "played_as": played_as,
                "decision": "win" if played_as == winner else "loss",
                "opponent_rank": opponent_rank,
                "OT": OT,
                "SO": SO,
                "total_goals_no_ot": (total_goals_no_ot - 1 if OT else total_goals_no_ot),
            })

        self.logger.log(3, "Team last 5 games parsed successfully", color=clr.GREEN)
        return games

    def get_new_games(self, for_tomorrow=False):
        re = req(urls.CALENDAR_URL)
        soup = BeautifulSoup(re.text, "html.parser")
        div = soup.find("div", attrs={"class": "b-table"})
        table = div.find("table")
        upcoming_games = table.find_all("tr", attrs={"class": "text-grey"})
        self.logger.log(2, "Started adding upcoming games", color=clr.CYAN, bold=True)

        for i, upcoming_game in enumerate(upcoming_games):
            if utils.check_if_date_is_valid(upcoming_game, for_tomorrow):
                a_element = upcoming_game.find("a")
                game_id_full = a_element.get("href").split("/")[-1]
                game_id = game_id_full.split("_")[1]
                self.get_new_single_game(game_id, i + 1)
            else:
                if utils.check_if_should_skip_game(upcoming_game, for_tomorrow):
                    continue
                self.logger.log(
                    1,
                    f"Finished parsing {i} games, next games are not for the specified date",
                    color=clr.ORANGE,
                )
                break

    def get_new_single_game(self, game_id, i):
        existing = (
            self.db.query(PhilipSnatKhlGame)
            .filter(PhilipSnatKhlGame.khl_id == int(game_id))
            .first()
        )
        if existing:
            self.logger.log(2, f"  Game {game_id} already in DB, skipping", color=clr.ORANGE)
            return

        re = req(urls.GAME_URL.replace("__GAME_ID__", game_id))
        game_info = self.retrieve_game_info_sportbox(re)
        home_name = game_info["home_team_name"]
        away_name = game_info["away_team_name"]
        date_str = game_info["date"]
        hour = game_info["hour"]

        self.logger.log(1, f"{i}. Game {home_name} vs {away_name}", color=clr.CYAN, bold=True)

        home_stats = self.get_team_stats_quant(home_name)
        away_stats = self.get_team_stats_quant(away_name)
        home_last_5 = self.get_team_last_5_games(home_name)
        away_last_5 = self.get_team_last_5_games(away_name)

        self._add_game_to_db(
            game_id, home_name, away_name, home_stats, away_stats,
            home_last_5, away_last_5, date_str, hour,
        )

    def _add_game_to_db(
        self, game_id, home_name, away_name, home_stats, away_stats,
        home_last_5, away_last_5, date_str, hour,
    ):
        home_last = home_last_5[0]
        away_last = away_last_5[0]
        h5lgw = sum(1 for g in home_last_5 if g.get("decision") == "win")
        a5lgw = sum(1 for g in away_last_5 if g.get("decision") == "win")

        try:
            game_date = datetime.datetime.strptime(date_str, "%d-%m-%Y").date()
        except ValueError:
            game_date = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()

        game = PhilipSnatKhlGame(
            khl_id=int(game_id),
            date=game_date,
            hour=hour,
            home_team=home_name,
            away_team=away_name,
            h_rank=int(home_stats.get("rank", 0)) if home_stats else None,
            a_rank=int(away_stats.get("rank", 0)) if away_stats else None,
            rank_diff=(int(home_stats.get("rank", 0)) - int(away_stats.get("rank", 0))) if home_stats and away_stats else None,
            h_gpg=utils.safe_float_conversion(home_stats.get("GpG", "")) if home_stats else None,
            a_gpg=utils.safe_float_conversion(away_stats.get("GpG", "")) if away_stats else None,
            gpg_diff=round(
                utils.safe_float_conversion(home_stats.get("GpG", ""))
                - utils.safe_float_conversion(away_stats.get("GpG", "")), 4
            ) if home_stats and away_stats else None,
            h_pk_pct=home_stats.get("PK%", "") if home_stats else None,
            a_pk_pct=away_stats.get("PK%", "") if away_stats else None,
            pk_pct_diff=round(
                utils.safe_float_conversion(home_stats.get("PK%", ""))
                - utils.safe_float_conversion(away_stats.get("PK%", "")), 4
            ) if home_stats and away_stats else None,
            h_pm_pg=home_stats.get("PMpG", "") if home_stats else None,
            a_pm_pg=away_stats.get("PMpG", "") if away_stats else None,
            pm_pg_diff=0.0,
            h_pp_pct=home_stats.get("PP%", "") if home_stats else None,
            a_pp_pct=away_stats.get("PP%", "") if away_stats else None,
            pp_pct_diff=round(
                utils.safe_float_conversion(home_stats.get("PP%", ""))
                - utils.safe_float_conversion(away_stats.get("PP%", "")), 4
            ) if home_stats and away_stats else None,
            h_ppg_apg=utils.safe_float_conversion(home_stats.get("PPGApG", "")) if home_stats else None,
            a_ppg_apg=utils.safe_float_conversion(away_stats.get("PPGApG", "")) if away_stats else None,
            ppg_apg_diff=round(
                utils.safe_float_conversion(home_stats.get("PPGApG", ""))
                - utils.safe_float_conversion(away_stats.get("PPGApG", "")), 4
            ) if home_stats and away_stats else None,
            h_sv_pct=home_stats.get("SV%", "") if home_stats else None,
            a_sv_pct=away_stats.get("SV%", "") if away_stats else None,
            sv_pct_diff=round(
                utils.safe_float_conversion(home_stats.get("SV%", ""))
                - utils.safe_float_conversion(away_stats.get("SV%", "")), 4
            ) if home_stats and away_stats else None,
            h_svpg=utils.safe_float_conversion(home_stats.get("SVpG", "")) if home_stats else None,
            a_svpg=utils.safe_float_conversion(away_stats.get("SVpG", "")) if away_stats else None,
            svpg_diff=round(
                utils.safe_float_conversion(home_stats.get("SVpG", ""))
                - utils.safe_float_conversion(away_stats.get("SVpG", "")), 4
            ) if home_stats and away_stats else None,
            h_spg=utils.safe_float_conversion(home_stats.get("SpG", "")) if home_stats else None,
            a_spg=utils.safe_float_conversion(away_stats.get("SpG", "")) if away_stats else None,
            spg_diff=round(
                utils.safe_float_conversion(home_stats.get("SpG", ""))
                - utils.safe_float_conversion(away_stats.get("SpG", "")), 4
            ) if home_stats and away_stats else None,
            h_lgd=home_last.get("decision"),
            a_lgd=away_last.get("decision"),
            h_lgpa=home_last.get("played_as"),
            a_lgpa=away_last.get("played_as"),
            h_lgop=str(home_last.get("opponent_rank", "")),
            a_lgop=str(away_last.get("opponent_rank", "")),
            lgop_diff=int(home_last.get("opponent_rank", 0)) - int(away_last.get("opponent_rank", 0)),
            h_l5gw=h5lgw,
            a_l5gw=a5lgw,
            l5gw_diff=h5lgw - a5lgw,
        )

        self.db.add(game)
        self.db.commit()
        self.logger.log(2, f"Added game {home_name} vs {away_name} to DB", color=clr.CYAN)

    def retrieve_game_info_sportbox(self, re, should_be_finished=False):
        soup = BeautifulSoup(re.text, "html.parser")
        div = soup.find("div", id="match_center_division")
        home_team_div = div.find("div", attrs={"class": "b-match__side_left"})
        away_team_div = div.find("div", attrs={"class": "b-match__side_right"})
        box_monitor = div.find("div", attrs={"class": "b-match__monitor"})
        date_span = box_monitor.find("span", attrs={"class": "match_count_date"})
        date_text = date_span.get_text().strip()
        date = date_text[0:10].replace(".", "-")

        hour = None
        br_tag = date_span.find("br")
        if br_tag:
            hour = br_tag.next_sibling.strip()

        home_team_name_sportbox = home_team_div.find("a", attrs={"class": "b-match__team-title"})
        away_team_name_sportbox = away_team_div.find("a", attrs={"class": "b-match__team-title"})
        home_name_text = home_team_name_sportbox.get_text().strip()
        away_name_text = away_team_name_sportbox.get_text().strip()

        if home_name_text == "Динамо":
            home_href = home_team_name_sportbox.get("href", "")
            home_name_text = "Динамо Москва" if "moscow" in home_href else "Динамо Минск"
        if away_name_text == "Динамо":
            away_href = away_team_name_sportbox.get("href", "")
            away_name_text = "Динамо Москва" if "moscow" in away_href else "Динамо Минск"

        home_team_name = team_sportbox_russian_name_map[home_name_text]
        away_team_name = team_sportbox_russian_name_map[away_name_text]

        home_score = away_score = winner = SO = OT = None
        home_score_no_ot = away_score_no_ot = total_score = total_score_no_ot = None

        if should_be_finished:
            score_span = box_monitor.find("span", attrs={"class": "b-match__monitor__count"})
            additional_info_div = box_monitor.find("div", attrs={"class": "b-match__additional-info"})

            if score_span:
                score_text = score_span.get_text().strip()
                scores = score_text.split(":")
                if scores[0].strip() != "-":
                    home_score = int(scores[0].strip())
                    away_score = int(scores[1].strip())
                    winner = "home" if home_score > away_score else "away"
                    additional_text = additional_info_div.get_text().strip() if additional_info_div else ""
                    SO = "б" in additional_text
                    OT = "ОТ" in additional_text
                    home_score_no_ot = home_score - 1 if ((OT or SO) and winner == "home") else home_score
                    away_score_no_ot = away_score - 1 if ((OT or SO) and winner == "away") else away_score
                    total_score = home_score + away_score
                    total_score_no_ot = home_score_no_ot + away_score_no_ot

        return {
            "home_team_name": home_team_name,
            "away_team_name": away_team_name,
            "date": date,
            "hour": hour,
            "home_score": home_score,
            "away_score": away_score,
            "home_score_no_ot": home_score_no_ot,
            "away_score_no_ot": away_score_no_ot,
            "winner": winner,
            "SO": SO,
            "OT": OT,
            "total_score": total_score,
            "total_score_no_ot": total_score_no_ot,
        }

    def fill_finished_games(self):
        games = (
            self.db.query(PhilipSnatKhlGame)
            .filter(PhilipSnatKhlGame.winner.is_(None))
            .order_by(PhilipSnatKhlGame.date.asc())
            .all()
        )
        self.logger.log(1, f"Started filling {len(games)} unfinished games", color=clr.CYAN, bold=True)

        for game in games:
            re = req(urls.GAME_URL.replace("__GAME_ID__", str(game.khl_id)))
            if not re:
                continue
            info = self.retrieve_game_info_sportbox(re, should_be_finished=True)

            if info["winner"] is None:
                self.logger.log(
                    1,
                    f"Game {game.date}: {game.home_team} vs {game.away_team} not finished yet",
                    color=clr.ORANGE,
                )
                continue

            game.winner = info["winner"]
            game.home_score = info["home_score"]
            game.away_score = info["away_score"]
            game.home_score_no_ot = info["home_score_no_ot"]
            game.away_score_no_ot = info["away_score_no_ot"]
            game.total_score = info["total_score"]
            game.total_score_no_ot = info["total_score_no_ot"]
            game.ot = info["OT"]
            game.so = info["SO"]

            self.db.commit()
            self.logger.log(
                2,
                f"Updated {game.home_team} vs {game.away_team}: {info['home_score']}:{info['away_score']}",
                color=clr.GREEN,
            )

        self.logger.log(1, "Finished filling games", color=clr.GREEN, bold=True)
