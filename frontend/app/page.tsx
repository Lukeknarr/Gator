'use client';

// Updated: Facebook-style login page with new catchphrase
import { useState, useEffect } from 'react';
import { useAuth } from '../hooks/useAuth';
import { useQuery } from '@tanstack/react-query';
import { api } from '../lib/api';
import { InterestGraph } from '../components/InterestGraph';
import { RecommendationFeed } from '../components/RecommendationFeed';
import { OnboardingModal } from '../components/OnboardingModal';
import LoginModal from '../components/LoginModal';
import RegisterModal from '../components/RegisterModal';
import ForgotPasswordModal from '../components/ForgotPasswordModal';

export default function Home() {
  const { user, isAuthenticated, login, register, logout } = useAuth();
  const [showOnboarding, setShowOnboarding] = useState(false);
  const [showLogin, setShowLogin] = useState(false);
  const [showRegister, setShowRegister] = useState(false);
  const [showForgotPassword, setShowForgotPassword] = useState(false);
  const [showTOS, setShowTOS] = useState(false);
  const [showPrivacy, setShowPrivacy] = useState(false);

  // Fetch user data when authenticated
  const { data: interests, isLoading: interestsLoading } = useQuery({
    queryKey: ['interests', user?.id],
    queryFn: () => api.get('/interests').then(res => res.data),
    enabled: !!isAuthenticated && !!user,
  });

  const { data: recommendations, isLoading: recommendationsLoading } = useQuery({
    queryKey: ['recommendations', user?.id],
    queryFn: () => api.get('/recommendations').then(res => res.data),
    enabled: !!isAuthenticated && !!user,
  });

  // Check if user needs onboarding
  useEffect(() => {
    if (isAuthenticated && user && (!interests?.data || interests.data.length === 0)) {
      setShowOnboarding(true);
    }
  }, [isAuthenticated, user, interests]);

  // If user is authenticated, show dashboard
  if (isAuthenticated && user) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-primary-50 to-secondary-50">
      {/* Header */}
        <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
                <h1 className="text-2xl font-bold text-primary-600">Gator</h1>
            </div>
            <div className="flex items-center space-x-4">
                <span className="text-sm text-gray-600">Welcome, {user.username}!</span>
                <button
                  onClick={logout}
                  className="btn-secondary"
                >
                  Sign Out
              </button>
            </div>
          </div>
        </div>
      </header>

        {/* Dashboard Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Stats Cards */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
            <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center">
                <div className="p-3 rounded-full bg-primary-100 text-primary-600">
                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                  </svg>
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-secondary-600">Interests</p>
                <p className="text-2xl font-bold text-secondary-900">
                    {interestsLoading ? '...' : interests?.data?.length || 0}
                </p>
              </div>
              </div>
            </div>

            <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center">
                <div className="p-3 rounded-full bg-secondary-100 text-secondary-600">
                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
              </div>
              <div className="ml-4">
                  <p className="text-sm font-medium text-secondary-600">Recommendations</p>
                  <p className="text-2xl font-bold text-secondary-900">
                    {recommendationsLoading ? '...' : recommendations?.data?.length || 0}
                  </p>
                </div>
              </div>
            </div>

            <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center">
                <div className="p-3 rounded-full bg-green-100 text-green-600">
                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
              </div>
              <div className="ml-4">
                  <p className="text-sm font-medium text-secondary-600">Active Time</p>
                  <p className="text-2xl font-bold text-secondary-900">2.5h</p>
                </div>
              </div>
            </div>
        </div>

          {/* Main Content Grid */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            {/* Recommendations */}
            <div className="bg-white rounded-lg shadow">
              <div className="p-6 border-b border-gray-200">
                <div className="flex items-center justify-between">
                  <h2 className="text-xl font-semibold text-gray-900">Your Recommendations</h2>
                  <button 
                    onClick={() => alert('View All functionality coming soon!')}
                    className="btn-primary"
                  >
                    View All
                  </button>
                </div>
              </div>
              <RecommendationFeed 
                recommendations={recommendations?.data || []}
                isLoading={recommendationsLoading}
              />
            </div>

            {/* Interest Graph */}
            <div className="bg-white rounded-lg shadow">
              <div className="p-6 border-b border-gray-200">
                <div className="flex items-center justify-between">
                  <h2 className="text-xl font-semibold text-gray-900">Your Interests</h2>
                  <button 
                    onClick={() => alert('Add Interest functionality coming soon!')}
                    className="btn-primary"
                  >
                    Add Interest
                  </button>
                </div>
              </div>
              <InterestGraph 
                interests={interests?.data || []}
                isLoading={interestsLoading}
              />
              </div>
            </div>
      </main>

        {/* Modals */}
      {showOnboarding && (
        <OnboardingModal
          isOpen={showOnboarding}
          onClose={() => setShowOnboarding(false)}
          />
        )}
      </div>
    );
  }

  // Login page for unauthenticated users
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center px-4">
      <div className="max-w-md w-full">
        {/* Logo and Catchphrase */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-blue-600 mb-2">Gator</h1>
          <p className="text-lg text-gray-600">Curating What Your Curiosity Deserves.</p>
        </div>

        {/* Login Form */}
        <div className="bg-white rounded-lg shadow-lg p-8">
          <form className="space-y-4">
            <div>
              <input
                type="text"
                placeholder="Email or username"
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-gray-900 placeholder-gray-500"
              />
            </div>
            <div>
              <input
                type="password"
                placeholder="Password"
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-gray-900 placeholder-gray-500"
              />
            </div>
            <button
              type="button"
              onClick={() => setShowLogin(true)}
              className="w-full bg-blue-600 text-white font-semibold py-3 px-4 rounded-lg hover:bg-blue-700 transition duration-200"
            >
              Log In
            </button>
          </form>

          <div className="mt-4 text-center">
            <button
              onClick={() => setShowForgotPassword(true)}
              className="text-blue-600 hover:text-blue-700 text-sm font-medium"
            >
              Forgot password?
            </button>
          </div>

          <div className="mt-6 pt-6 border-t border-gray-200">
            <button
              onClick={() => setShowRegister(true)}
              className="w-full bg-green-600 text-white font-semibold py-3 px-4 rounded-lg hover:bg-green-700 transition duration-200"
            >
              Create new account
            </button>
          </div>
        </div>

        {/* Footer */}
        <div className="mt-8 text-center text-sm text-gray-500">
          <p>
            By continuing, you agree to Gator's{' '}
            <button 
              onClick={() => setShowTOS(true)}
              className="text-blue-600 hover:text-blue-700 underline"
            >
              Terms of Service
            </button>
            {' '}and{' '}
            <button 
              onClick={() => setShowPrivacy(true)}
              className="text-blue-600 hover:text-blue-700 underline"
            >
              Privacy Policy
            </button>
            .
          </p>
        </div>
      </div>

      {/* Modals */}
      {showLogin && (
        <LoginModal
          isOpen={showLogin}
          onClose={() => setShowLogin(false)}
          onSwitchToRegister={() => {
            setShowLogin(false);
            setShowRegister(true);
          }}
        />
      )}

      {showRegister && (
        <RegisterModal
          isOpen={showRegister}
          onClose={() => setShowRegister(false)}
          onSwitchToLogin={() => {
            setShowRegister(false);
            setShowLogin(true);
          }}
        />
      )}

      {showForgotPassword && (
        <ForgotPasswordModal
          isOpen={showForgotPassword}
          onClose={() => setShowForgotPassword(false)}
        />
      )}

      {/* Terms of Service Modal */}
      {showTOS && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-xl max-w-4xl w-full mx-4 max-h-[80vh] overflow-y-auto">
            <div className="p-6 border-b border-gray-200">
              <div className="flex items-center justify-between">
                <h2 className="text-xl font-semibold text-gray-900">Terms of Service</h2>
                <button
                  onClick={() => setShowTOS(false)}
                  className="text-gray-400 hover:text-gray-600 transition-colors"
                >
                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
            </div>
            <div className="p-6">
              <div className="prose max-w-none text-sm">
                <h3 className="text-lg font-semibold mb-4">GATOR TECHNOLOGIES, INC.</h3>
                <h4 className="text-md font-semibold mb-2">TERMS OF SERVICE AND PRIVACY POLICY</h4>
                <p className="mb-4">Effective Date: August 1, 2024</p>
                
                <h5 className="font-semibold mt-6 mb-2">1. AGREEMENT TO TERMS</h5>
                <p className="mb-4">These Terms of Service ("Terms") constitute a legally binding agreement made between you ("User," "you") and Gator Technologies, Inc. ("Gator," "Company," "we," "our," or "us") concerning your access to and use of the Gator website, platform, and related services (collectively, the "Service"). By creating an account, accessing, or using our Service, you agree to be bound by these Terms and our Privacy Policy.</p>
                
                <h5 className="font-semibold mt-6 mb-2">2. ELIGIBILITY</h5>
                <p className="mb-4">You represent and warrant that you are at least 16 years of age (or the legal age of digital consent in your jurisdiction) and have the authority to enter into these Terms.</p>
                
                <h5 className="font-semibold mt-6 mb-2">3. SERVICE DESCRIPTION</h5>
                <p className="mb-4">Gator provides a media discovery and recommendation platform that aggregates information about your interests and media consumption patterns to deliver personalized recommendations across multiple content sources.</p>
                
                <h5 className="font-semibold mt-6 mb-2">4. ACCOUNT REGISTRATION AND SECURITY</h5>
                <p className="mb-4">You are responsible for maintaining the confidentiality of your login credentials and for all activities under your account. You must notify Gator immediately of any unauthorized access.</p>
                
                <h5 className="font-semibold mt-6 mb-2">5. USER CONTENT AND DATA</h5>
                <p className="mb-4">You retain ownership of the data and content you submit to the Service. By using the Service, you grant Gator a non-exclusive, worldwide, royalty-free license to process, analyze, and display User Content solely to provide and improve the Service.</p>
                
                <h5 className="font-semibold mt-6 mb-2">6. ACCEPTABLE USE</h5>
                <p className="mb-4">You agree not to access the Service using automated tools, reverse-engineer any part of the Service, or use the Service to violate any law or infringe the rights of others.</p>
                
                <h5 className="font-semibold mt-6 mb-2">7. SERVICE AVAILABILITY</h5>
                <p className="mb-4">The Service is provided "AS IS" and "AS AVAILABLE" without warranties of any kind, whether express or implied.</p>
                
                <h5 className="font-semibold mt-6 mb-2">8. LIMITATION OF LIABILITY</h5>
                <p className="mb-4">To the maximum extent permitted by law, Gator shall not be liable for indirect, incidental, consequential, or punitive damages. Total liability shall not exceed $100 USD.</p>
                
                <h5 className="font-semibold mt-6 mb-2">9. CONTACT INFORMATION</h5>
                <p className="mb-4">Email: legal@gatorapp.com</p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Privacy Policy Modal */}
      {showPrivacy && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-xl max-w-4xl w-full mx-4 max-h-[80vh] overflow-y-auto">
            <div className="p-6 border-b border-gray-200">
              <div className="flex items-center justify-between">
                <h2 className="text-xl font-semibold text-gray-900">Privacy Policy</h2>
                <button
                  onClick={() => setShowPrivacy(false)}
                  className="text-gray-400 hover:text-gray-600 transition-colors"
                >
                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
            </div>
            <div className="p-6">
              <div className="prose max-w-none text-sm">
                <h3 className="text-lg font-semibold mb-4">PRIVACY POLICY</h3>
                <p className="mb-4">Effective Date: August 1, 2024</p>
                
                <h5 className="font-semibold mt-6 mb-2">1. INFORMATION WE COLLECT</h5>
                <ul className="list-disc pl-6 mb-4">
                  <li>Personal Information: Email, name, login credentials, account preferences</li>
                  <li>Usage Data: Pages viewed, interests tracked, recommendation interactions</li>
                  <li>Third-party Integrations: Data pulled from connected services with your explicit consent</li>
                </ul>
                
                <h5 className="font-semibold mt-6 mb-2">2. HOW WE USE YOUR INFORMATION</h5>
                <ul className="list-disc pl-6 mb-4">
                  <li>To provide and improve the Service</li>
                  <li>To personalize content recommendations</li>
                  <li>For analytics, debugging, and research purposes</li>
                  <li>To comply with legal obligations</li>
                </ul>
                
                <h5 className="font-semibold mt-6 mb-2">3. DATA SHARING</h5>
                <p className="mb-4">We do not sell personal data. We may share aggregated, anonymized analytics with partners and may share information with vendors, service providers, and legal authorities as required.</p>
                
                <h5 className="font-semibold mt-6 mb-2">4. DATA STORAGE AND SECURITY</h5>
                <p className="mb-4">Data is stored securely in encrypted databases. Access is limited to authorized personnel only. No system is 100% secure; you use the Service at your own risk.</p>
                
                <h5 className="font-semibold mt-6 mb-2">5. USER RIGHTS (GDPR / CCPA)</h5>
                <p className="mb-4">You have the right to access, rectify, or delete your personal data. You may opt-out of certain processing or marketing communications. Requests can be made to privacy@gatorapp.com.</p>
                
                <h5 className="font-semibold mt-6 mb-2">6. COOKIES AND TRACKING</h5>
                <p className="mb-4">We use cookies for essential functionality and analytics. You may disable cookies but some features may not work properly.</p>
                
                <h5 className="font-semibold mt-6 mb-2">7. DATA RETENTION</h5>
                <p className="mb-4">We retain user data as long as your account is active or as necessary to provide the Service. Data may be retained longer to comply with legal obligations.</p>
                
                <h5 className="font-semibold mt-6 mb-2">8. CONTACT</h5>
                <p className="mb-4">privacy@gatorapp.com</p>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
} 