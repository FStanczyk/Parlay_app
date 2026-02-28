from philip_snat_models.khl.const import clr


class Logger:
    def __init__(self, verbose=1):
        self.verbose = verbose

    def log(self, verbose_level, message, color=None, bold=False, dim=False):
        if verbose_level <= self.verbose:
            if color:
                message = color + message + clr.END
            if bold:
                message = clr.BOLD + message + clr.END
            if dim:
                message = clr.DIM + message + clr.END
            print(message)

    def log_error(self, verbose_level, message):
        if verbose_level <= self.verbose:
            print(clr.RED + message + clr.END)
