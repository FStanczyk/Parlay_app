import { Route, BrowserRouter as Router, Routes, Navigate } from 'react-router-dom';
import Features from './components/Features';
import Footer from './components/Footer';
import Navbar from './components/Navbar';
import ProtectedRoute from './components/ProtectedRoute';
import { AuthProvider } from './contexts/AuthContext';
import { TranslationProvider } from './contexts/TranslationContext';
import BecomeExpert from './pages/BecomeExpert';
import Dashboard from './pages/Dashboard';
import ExpertPanel from './pages/ExpertPanel';
import Hub from './pages/Hub';
import PhilipSnatModels from './pages/PhilipSnatModels';
import PhilipSnatModelView from './pages/PhilipSnatModelView';
import AdminPanel from './pages/AdminPanel';
import AddAIPredictions from './pages/AdminPanelPages/AddAIPredictions';
import Users from './pages/AdminPanelPages/Users';
import EditProfile from './pages/ExpertPanelPages/EditProfile';
import ManageMonetization from './pages/ExpertPanelPages/ManageMonetization';
import AddRecommendation from './pages/ExpertPanelPages/AddRecommendation';
import EditRecommendation from './pages/ExpertPanelPages/EditRecommendation';
import ManageRecommendations from './pages/ExpertPanelPages/ManageRecommendations';
import ExpertStatistics from './pages/ExpertPanelPages/Statistics';
import Generator from './pages/Generator';
import Home from './pages/Home';
import Login from './pages/Login';
import MyParlays from './pages/MyCoupons';
import Plans from './pages/Plans';
import Recommendations from './pages/Recommendations';
import Register from './pages/Register';
import SearchExperts from './pages/SearchExpertPages/SearchExperts';
import ExpertProfile from './pages/SearchExpertPages/ExpertProfile';
import Settings from './pages/Settings';
import Simulator from './pages/Simulator';
import Stats from './pages/Stats';

function App() {
  return (
    <TranslationProvider>
      <AuthProvider>
        <Router>
        <div className="app">
          <Navbar />
          <main className="main">
            <Routes>
              <Route path="/" element={<Home />} />
              <Route path="/philip-snat-models" element={<PhilipSnatModels />} />
              <Route path="/philip-snat-models/:file_id" element={<PhilipSnatModelView />} />
              <Route
                path="/hub"
                element={
                  <ProtectedRoute>
                    <Hub />
                  </ProtectedRoute>
                }
              />
              <Route path="/generator" element={<Generator />} />
              <Route path="/login" element={<Login />} />
              <Route path="/register" element={<Register />} />
              <Route path="/plans" element={<Plans />} />
              <Route
                path="/become-expert"
                element={
                  <ProtectedRoute>
                    <BecomeExpert />
                  </ProtectedRoute>
                }
              />
              <Route
                path="/expert-panel"
                element={
                  <ProtectedRoute>
                    <ExpertPanel />
                  </ProtectedRoute>
                }
              />
              <Route
                path="/expert-panel/edit-profile"
                element={
                  <ProtectedRoute>
                    <EditProfile />
                  </ProtectedRoute>
                }
              />
              <Route
                path="/expert-panel/recommendations"
                element={
                  <ProtectedRoute>
                    <ManageRecommendations />
                  </ProtectedRoute>
                }
              />
              <Route
                path="/expert-panel/recommendations/add"
                element={
                  <ProtectedRoute>
                    <AddRecommendation />
                  </ProtectedRoute>
                }
              />
              <Route
                path="/expert-panel/recommendations/edit/:id"
                element={
                  <ProtectedRoute>
                    <EditRecommendation />
                  </ProtectedRoute>
                }
              />
              <Route
                path="/expert-panel/monetization"
                element={
                  <ProtectedRoute>
                    <ManageMonetization />
                  </ProtectedRoute>
                }
              />
              <Route
                path="/expert-panel/statistics"
                element={
                  <ProtectedRoute>
                    <ExpertStatistics />
                  </ProtectedRoute>
                }
              />
              <Route
                path="/admin-panel"
                element={
                  <ProtectedRoute>
                    <AdminPanel />
                  </ProtectedRoute>
                }
              >
                <Route
                  index
                  element={<Navigate to="/admin-panel/add-ai-predictions" replace />}
                />
                <Route
                  path="add-ai-predictions"
                  element={<AddAIPredictions />}
                />
                <Route
                  path="users"
                  element={<Users />}
                />
              </Route>
              <Route
                path="/experts/search"
                element={
                  <ProtectedRoute>
                    <SearchExperts />
                  </ProtectedRoute>
                }
              />
              <Route
                path="/experts/:id"
                element={
                  <ProtectedRoute>
                    <ExpertProfile />
                  </ProtectedRoute>
                }
              />
              <Route
                path="/experts/recommendations"
                element={
                  <ProtectedRoute>
                    <Recommendations />
                  </ProtectedRoute>
                }
              />
              <Route
                path="/simulator"
                element={
                  <ProtectedRoute>
                    <Simulator />
                  </ProtectedRoute>
                }
              />
              <Route
                path="/profile/dashboard"
                element={
                  <ProtectedRoute>
                    <Dashboard />
                  </ProtectedRoute>
                }
              />
              <Route
                path="/profile/parlays"
                element={
                  <ProtectedRoute>
                    <MyParlays />
                  </ProtectedRoute>
                }
              />
              <Route
                path="/profile/stats"
                element={
                  <ProtectedRoute>
                    <Stats />
                  </ProtectedRoute>
                }
              />
              <Route
                path="/profile/settings"
                element={
                  <ProtectedRoute>
                    <Settings />
                  </ProtectedRoute>
                }
              />
              <Route
                path="/dashboard"
                element={
                  <ProtectedRoute>
                    <Dashboard />
                  </ProtectedRoute>
                }
              />
              <Route
                path="/pro-features"
                element={
                  <ProtectedRoute requireSubscription requirePlan={1}>
                    <Features type="pro" />
                  </ProtectedRoute>
                }
              />
              <Route
                path="/elite-features"
                element={
                  <ProtectedRoute requireSubscription requirePlan={0}>
                    <Features type="basic" />
                  </ProtectedRoute>
                }
              />
            </Routes>
          </main>
          <Footer />
        </div>
      </Router>
      </AuthProvider>
    </TranslationProvider>
  );
}

export default App;
