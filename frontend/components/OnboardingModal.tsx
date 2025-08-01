'use client';

import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, Check, ArrowRight } from 'lucide-react';
import { useAuth } from '@/hooks/useAuth';
import { api } from '@/lib/api';
import toast from 'react-hot-toast';

interface OnboardingModalProps {
  isOpen: boolean;
  onClose: () => void;
}

const SUGGESTED_INTERESTS = [
  'artificial intelligence',
  'machine learning',
  'climate change',
  'startups',
  'technology',
  'politics',
  'science',
  'business',
  'health',
  'education',
  'environment',
  'finance',
  'psychology',
  'philosophy',
  'history',
  'art',
  'music',
  'sports',
  'travel',
  'cooking'
];

const READING_PREFERENCES = [
  { id: 'articles', label: 'Articles', icon: '📰' },
  { id: 'podcasts', label: 'Podcasts', icon: '🎧' },
  { id: 'videos', label: 'Videos', icon: '📺' },
  { id: 'papers', label: 'Academic Papers', icon: '📚' }
];

const EXPLORATION_LEVELS = [
  { id: 'conservative', label: 'Conservative', description: 'Stick to familiar topics' },
  { id: 'balanced', label: 'Balanced', description: 'Mix of familiar and new topics' },
  { id: 'adventurous', label: 'Adventurous', description: 'Explore diverse topics' }
];

export function OnboardingModal({ isOpen, onClose }: OnboardingModalProps) {
  const { user } = useAuth();
  const [step, setStep] = useState(1);
  const [selectedInterests, setSelectedInterests] = useState<string[]>([]);
  const [customInterest, setCustomInterest] = useState('');
  const [readingPreferences, setReadingPreferences] = useState<string[]>([]);
  const [explorationLevel, setExplorationLevel] = useState('balanced');
  const [timeAvailability, setTimeAvailability] = useState('medium');
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleInterestToggle = (interest: string) => {
    setSelectedInterests(prev => 
      prev.includes(interest)
        ? prev.filter(i => i !== interest)
        : [...prev, interest]
    );
  };

  const handleAddCustomInterest = () => {
    if (customInterest.trim() && !selectedInterests.includes(customInterest.trim())) {
      setSelectedInterests(prev => [...prev, customInterest.trim()]);
      setCustomInterest('');
    }
  };

  const handleReadingPreferenceToggle = (preference: string) => {
    setReadingPreferences(prev => 
      prev.includes(preference)
        ? prev.filter(p => p !== preference)
        : [...prev, preference]
    );
  };

  const handleSubmit = async () => {
    if (selectedInterests.length === 0) {
      toast.error('Please select at least one interest');
      return;
    }

    if (readingPreferences.length === 0) {
      toast.error('Please select at least one reading preference');
      return;
    }

    setIsSubmitting(true);
    try {
      await api.post('/onboarding', {
        interests: selectedInterests,
        reading_preferences: readingPreferences,
        time_availability: timeAvailability,
        exploration_level: explorationLevel,
      });

      toast.success('Onboarding completed!');
      onClose();
    } catch (error) {
      console.error('Onboarding failed:', error);
      toast.error('Failed to complete onboarding');
    } finally {
      setIsSubmitting(false);
    }
  };

  const nextStep = () => {
    if (step === 1 && selectedInterests.length === 0) {
      toast.error('Please select at least one interest');
      return;
    }
    if (step === 2 && readingPreferences.length === 0) {
      toast.error('Please select at least one reading preference');
      return;
    }
    setStep(step + 1);
  };

  const prevStep = () => {
    setStep(step - 1);
  };

  return (
    <AnimatePresence>
      {isOpen && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50"
          onClick={onClose}
        >
          <motion.div
            initial={{ scale: 0.9, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            exit={{ scale: 0.9, opacity: 0 }}
            className="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto"
            onClick={(e) => e.stopPropagation()}
          >
            {/* Header */}
            <div className="flex items-center justify-between p-6 border-b border-secondary-200">
              <h2 className="text-2xl font-bold text-secondary-900">
                Welcome to Gator, {user?.username}!
              </h2>
              <button
                onClick={onClose}
                className="p-2 hover:bg-secondary-100 rounded-lg transition-colors"
              >
                <X className="h-5 w-5 text-secondary-600" />
              </button>
            </div>

            {/* Progress Bar */}
            <div className="px-6 py-4">
              <div className="flex items-center space-x-2">
                {[1, 2, 3].map((stepNumber) => (
                  <div key={stepNumber} className="flex items-center">
                    <div
                      className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium ${
                        step >= stepNumber
                          ? 'bg-primary-600 text-white'
                          : 'bg-secondary-200 text-secondary-600'
                      }`}
                    >
                      {step > stepNumber ? <Check className="h-4 w-4" /> : stepNumber}
                    </div>
                    {stepNumber < 3 && (
                      <div
                        className={`w-12 h-1 mx-2 ${
                          step > stepNumber ? 'bg-primary-600' : 'bg-secondary-200'
                        }`}
                      />
                    )}
                  </div>
                ))}
              </div>
            </div>

            {/* Content */}
            <div className="px-6 pb-6">
              {step === 1 && (
                <motion.div
                  initial={{ opacity: 0, x: 20 }}
                  animate={{ opacity: 1, x: 0 }}
                  className="space-y-6"
                >
                  <div>
                    <h3 className="text-xl font-semibold text-secondary-900 mb-2">
                      What interests you?
                    </h3>
                    <p className="text-secondary-600">
                      Select topics you're interested in. We'll use this to personalize your recommendations.
                    </p>
                  </div>

                  <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
                    {SUGGESTED_INTERESTS.map((interest) => (
                      <button
                        key={interest}
                        onClick={() => handleInterestToggle(interest)}
                        className={`p-3 rounded-lg border-2 text-left transition-all ${
                          selectedInterests.includes(interest)
                            ? 'border-primary-500 bg-primary-50 text-primary-700'
                            : 'border-secondary-200 hover:border-primary-300'
                        }`}
                      >
                        {interest}
                      </button>
                    ))}
                  </div>

                  <div className="space-y-3">
                    <label className="block text-sm font-medium text-secondary-700">
                      Add custom interest
                    </label>
                    <div className="flex space-x-2">
                      <input
                        type="text"
                        value={customInterest}
                        onChange={(e) => setCustomInterest(e.target.value)}
                        placeholder="Enter a topic..."
                        className="input-field flex-1"
                        onKeyPress={(e) => e.key === 'Enter' && handleAddCustomInterest()}
                      />
                      <button
                        onClick={handleAddCustomInterest}
                        className="btn-primary"
                      >
                        Add
                      </button>
                    </div>
                  </div>

                  {selectedInterests.length > 0 && (
                    <div className="flex flex-wrap gap-2">
                      {selectedInterests.map((interest) => (
                        <span
                          key={interest}
                          className="badge badge-primary"
                        >
                          {interest}
                          <button
                            onClick={() => handleInterestToggle(interest)}
                            className="ml-1 hover:text-primary-800"
                          >
                            ×
                          </button>
                        </span>
                      ))}
                    </div>
                  )}
                </motion.div>
              )}

              {step === 2 && (
                <motion.div
                  initial={{ opacity: 0, x: 20 }}
                  animate={{ opacity: 1, x: 0 }}
                  className="space-y-6"
                >
                  <div>
                    <h3 className="text-xl font-semibold text-secondary-900 mb-2">
                      How do you like to consume content?
                    </h3>
                    <p className="text-secondary-600">
                      Select your preferred content types.
                    </p>
                  </div>

                  <div className="grid grid-cols-2 gap-4">
                    {READING_PREFERENCES.map((preference) => (
                      <button
                        key={preference.id}
                        onClick={() => handleReadingPreferenceToggle(preference.id)}
                        className={`p-4 rounded-lg border-2 text-center transition-all ${
                          readingPreferences.includes(preference.id)
                            ? 'border-primary-500 bg-primary-50 text-primary-700'
                            : 'border-secondary-200 hover:border-primary-300'
                        }`}
                      >
                        <div className="text-2xl mb-2">{preference.icon}</div>
                        <div className="font-medium">{preference.label}</div>
                      </button>
                    ))}
                  </div>
                </motion.div>
              )}

              {step === 3 && (
                <motion.div
                  initial={{ opacity: 0, x: 20 }}
                  animate={{ opacity: 1, x: 0 }}
                  className="space-y-6"
                >
                  <div>
                    <h3 className="text-xl font-semibold text-secondary-900 mb-2">
                      Customize your experience
                    </h3>
                    <p className="text-secondary-600">
                      Tell us about your preferences for content discovery.
                    </p>
                  </div>

                  <div className="space-y-4">
                    <div>
                      <label className="block text-sm font-medium text-secondary-700 mb-2">
                        Exploration Level
                      </label>
                      <div className="space-y-2">
                        {EXPLORATION_LEVELS.map((level) => (
                          <button
                            key={level.id}
                            onClick={() => setExplorationLevel(level.id)}
                            className={`w-full p-3 rounded-lg border-2 text-left transition-all ${
                              explorationLevel === level.id
                                ? 'border-primary-500 bg-primary-50 text-primary-700'
                                : 'border-secondary-200 hover:border-primary-300'
                            }`}
                          >
                            <div className="font-medium">{level.label}</div>
                            <div className="text-sm text-secondary-600">{level.description}</div>
                          </button>
                        ))}
                      </div>
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-secondary-700 mb-2">
                        Time Availability
                      </label>
                      <select
                        value={timeAvailability}
                        onChange={(e) => setTimeAvailability(e.target.value)}
                        className="input-field"
                      >
                        <option value="low">Low (5-15 minutes/day)</option>
                        <option value="medium">Medium (15-30 minutes/day)</option>
                        <option value="high">High (30+ minutes/day)</option>
                      </select>
                    </div>
                  </div>
                </motion.div>
              )}
            </div>

            {/* Footer */}
            <div className="flex items-center justify-between p-6 border-t border-secondary-200">
              <button
                onClick={step === 1 ? onClose : prevStep}
                className="btn-secondary"
              >
                {step === 1 ? 'Skip' : 'Back'}
              </button>

              <div className="flex space-x-3">
                {step < 3 ? (
                  <button
                    onClick={nextStep}
                    className="btn-primary"
                  >
                    Next
                    <ArrowRight className="h-4 w-4 ml-2" />
                  </button>
                ) : (
                  <button
                    onClick={handleSubmit}
                    disabled={isSubmitting}
                    className="btn-primary"
                  >
                    {isSubmitting ? 'Setting up...' : 'Complete Setup'}
                  </button>
                )}
              </div>
            </div>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
} 