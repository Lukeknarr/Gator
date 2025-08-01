'use client';

import { useState, useEffect } from 'react';
import { useQuery } from 'react-query';
import { motion } from 'framer-motion';
import { 
  Brain, 
  TrendingUp, 
  Search, 
  BookOpen, 
  Users, 
  Settings,
  Plus,
  Filter
} from 'lucide-react';
import { InterestGraph } from '@/components/InterestGraph';
import { RecommendationFeed } from '@/components/RecommendationFeed';
import { OnboardingModal } from '@/components/OnboardingModal';
import { useAuth } from '@/hooks/useAuth';
import { api } from '@/lib/api';

export default function Dashboard() {
  const { user, isAuthenticated } = useAuth();
  const [showOnboarding, setShowOnboarding] = useState(false);
  const [activeTab, setActiveTab] = useState('recommendations');

  // Fetch user interests
  const { data: interests, isLoading: interestsLoading } = useQuery(
    ['interests', user?.id],
    () => api.get('/interests'),
    {
      enabled: !!user?.id,
    }
  );

  // Fetch recommendations
  const { data: recommendations, isLoading: recommendationsLoading, refetch: refetchRecommendations } = useQuery(
    ['recommendations', user?.id],
    () => api.get('/recommendations'),
    {
      enabled: !!user?.id,
    }
  );

  // Check if user needs onboarding
  useEffect(() => {
    if (isAuthenticated && user && (!interests?.data || interests.data.length === 0)) {
      setShowOnboarding(true);
    }
  }, [isAuthenticated, user, interests]);

  if (!isAuthenticated) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-primary-50 to-secondary-50">
        <div className="text-center">
          <h1 className="text-4xl font-bold text-primary-600 mb-4">Welcome to Gator</h1>
          <p className="text-secondary-600 mb-8">Please log in to access your personalized dashboard</p>
          <button className="btn-primary">Sign In</button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-secondary-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-secondary-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
              <Brain className="h-8 w-8 text-primary-600 mr-3" />
              <h1 className="text-xl font-semibold text-secondary-900">Gator</h1>
            </div>
            
            <div className="flex items-center space-x-4">
              <button className="btn-secondary">
                <Search className="h-4 w-4 mr-2" />
                Search
              </button>
              <button className="btn-secondary">
                <Settings className="h-4 w-4 mr-2" />
                Settings
              </button>
              <div className="flex items-center space-x-2">
                <div className="w-8 h-8 bg-primary-600 rounded-full flex items-center justify-center">
                  <span className="text-white text-sm font-medium">
                    {user?.username?.charAt(0).toUpperCase()}
                  </span>
                </div>
                <span className="text-secondary-700">{user?.username}</span>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="card"
          >
            <div className="flex items-center">
              <div className="p-2 bg-primary-100 rounded-lg">
                <Brain className="h-6 w-6 text-primary-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-secondary-600">Interests</p>
                <p className="text-2xl font-bold text-secondary-900">
                  {interestsLoading ? '...' : interests?.data?.length || 0}
                </p>
              </div>
            </div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="card"
          >
            <div className="flex items-center">
              <div className="p-2 bg-green-100 rounded-lg">
                <BookOpen className="h-6 w-6 text-green-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-secondary-600">Articles Read</p>
                <p className="text-2xl font-bold text-secondary-900">24</p>
              </div>
            </div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
            className="card"
          >
            <div className="flex items-center">
              <div className="p-2 bg-yellow-100 rounded-lg">
                <TrendingUp className="h-6 w-6 text-yellow-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-secondary-600">Exploration Score</p>
                <p className="text-2xl font-bold text-secondary-900">78%</p>
              </div>
            </div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4 }}
            className="card"
          >
            <div className="flex items-center">
              <div className="p-2 bg-purple-100 rounded-lg">
                <Users className="h-6 w-6 text-purple-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-secondary-600">Connections</p>
                <p className="text-2xl font-bold text-secondary-900">12</p>
              </div>
            </div>
          </motion.div>
        </div>

        {/* Tabs */}
        <div className="flex space-x-1 bg-white p-1 rounded-lg shadow-sm mb-8">
          <button
            onClick={() => setActiveTab('recommendations')}
            className={`flex-1 py-2 px-4 rounded-md text-sm font-medium transition-colors ${
              activeTab === 'recommendations'
                ? 'bg-primary-100 text-primary-700'
                : 'text-secondary-600 hover:text-secondary-900'
            }`}
          >
            Recommendations
          </button>
          <button
            onClick={() => setActiveTab('graph')}
            className={`flex-1 py-2 px-4 rounded-md text-sm font-medium transition-colors ${
              activeTab === 'graph'
                ? 'bg-primary-100 text-primary-700'
                : 'text-secondary-600 hover:text-secondary-900'
            }`}
          >
            Interest Graph
          </button>
          <button
            onClick={() => setActiveTab('explore')}
            className={`flex-1 py-2 px-4 rounded-md text-sm font-medium transition-colors ${
              activeTab === 'explore'
                ? 'bg-primary-100 text-primary-700'
                : 'text-secondary-600 hover:text-secondary-900'
            }`}
          >
            Explore
          </button>
        </div>

        {/* Content */}
        <motion.div
          key={activeTab}
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.3 }}
        >
          {activeTab === 'recommendations' && (
            <div className="space-y-6">
              <div className="flex justify-between items-center">
                <h2 className="text-2xl font-bold text-secondary-900">Your Recommendations</h2>
                <button
                  onClick={() => refetchRecommendations()}
                  className="btn-secondary"
                >
                  <Filter className="h-4 w-4 mr-2" />
                  Refresh
                </button>
              </div>
              <RecommendationFeed 
                recommendations={recommendations?.data || []}
                isLoading={recommendationsLoading}
              />
            </div>
          )}

          {activeTab === 'graph' && (
            <div className="space-y-6">
              <div className="flex justify-between items-center">
                <h2 className="text-2xl font-bold text-secondary-900">Interest Graph</h2>
                <button className="btn-primary">
                  <Plus className="h-4 w-4 mr-2" />
                  Add Interest
                </button>
              </div>
              <InterestGraph 
                interests={interests?.data || []}
                isLoading={interestsLoading}
              />
            </div>
          )}

          {activeTab === 'explore' && (
            <div className="space-y-6">
              <h2 className="text-2xl font-bold text-secondary-900">Explore New Topics</h2>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {/* Exploration content will go here */}
                <div className="card">
                  <h3 className="text-lg font-semibold mb-2">Discover Cross-Domain Connections</h3>
                  <p className="text-secondary-600 mb-4">
                    Find content that bridges your different interests
                  </p>
                  <button className="btn-primary">Explore</button>
                </div>
              </div>
            </div>
          )}
        </motion.div>
      </main>

      {/* Onboarding Modal */}
      {showOnboarding && (
        <OnboardingModal
          isOpen={showOnboarding}
          onClose={() => setShowOnboarding(false)}
        />
      )}
    </div>
  );
} 