'use client';

import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  ExternalLink, 
  ThumbsUp, 
  ThumbsDown, 
  Share2, 
  Bookmark,
  Clock,
  User,
  Tag
} from 'lucide-react';
import { api } from '@/lib/api';
import toast from 'react-hot-toast';

interface Content {
  id: number;
  title: string;
  url: string;
  source: string;
  author: string;
  published_at: string;
  summary: string;
  content_type: string;
  tags: Array<{ id: number; name: string; category: string }>;
  created_at: string;
}

interface RecommendationFeedProps {
  recommendations: Content[];
  isLoading: boolean;
}

export function RecommendationFeed({ recommendations, isLoading }: RecommendationFeedProps) {
  const [interactingContent, setInteractingContent] = useState<number | null>(null);

  const handleFeedback = async (contentId: number, interactionType: 'like' | 'dislike' | 'view' | 'share') => {
    try {
      setInteractingContent(contentId);
      
      await api.post('/feedback', {
        content_id: contentId,
        interaction_type: interactionType,
      });

      toast.success('Feedback recorded!');
    } catch (error) {
      console.error('Failed to submit feedback:', error);
      toast.error('Failed to record feedback');
    } finally {
      setInteractingContent(null);
    }
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffInHours = Math.floor((now.getTime() - date.getTime()) / (1000 * 60 * 60));
    
    if (diffInHours < 1) return 'Just now';
    if (diffInHours < 24) return `${diffInHours}h ago`;
    if (diffInHours < 168) return `${Math.floor(diffInHours / 24)}d ago`;
    return date.toLocaleDateString();
  };

  const getSourceIcon = (source: string) => {
    switch (source.toLowerCase()) {
      case 'rss':
        return '📰';
      case 'substack':
        return '📧';
      case 'arxiv':
        return '📚';
      case 'youtube':
        return '📺';
      default:
        return '📄';
    }
  };

  const getContentTypeColor = (contentType: string) => {
    switch (contentType.toLowerCase()) {
      case 'article':
        return 'bg-blue-100 text-blue-800';
      case 'podcast':
        return 'bg-purple-100 text-purple-800';
      case 'video':
        return 'bg-red-100 text-red-800';
      case 'paper':
        return 'bg-green-100 text-green-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  if (isLoading) {
    return (
      <div className="space-y-4">
        {[...Array(5)].map((_, i) => (
          <div key={i} className="card">
            <div className="loading-pulse h-4 w-3/4 mb-2"></div>
            <div className="loading-pulse h-3 w-1/2 mb-4"></div>
            <div className="loading-pulse h-20 w-full"></div>
          </div>
        ))}
      </div>
    );
  }

  if (!recommendations.length) {
    return (
      <div className="card text-center py-12">
        <h3 className="text-lg font-medium text-gray-900 mb-2">
          No recommendations yet
        </h3>
        <p className="text-gray-600 mb-4">
          We're learning your preferences. Check back soon for personalized content!
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <AnimatePresence>
        {recommendations.map((content, index) => (
          <motion.div
            key={content.id}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            transition={{ delay: index * 0.1 }}
            className="card hover:shadow-md transition-shadow duration-200"
          >
            {/* Header */}
            <div className="flex items-start justify-between mb-4">
              <div className="flex items-center space-x-2">
                <span className="text-lg">{getSourceIcon(content.source)}</span>
                <div>
                  <h3 className="text-lg font-semibold text-secondary-900 line-clamp-2">
                    {content.title}
                  </h3>
                  <div className="flex items-center space-x-4 text-sm text-secondary-600 mt-1">
                    {content.author && (
                      <div className="flex items-center">
                        <User className="h-3 w-3 mr-1" />
                        {content.author}
                      </div>
                    )}
                    <div className="flex items-center">
                      <Clock className="h-3 w-3 mr-1" />
                      {formatDate(content.published_at || content.created_at)}
                    </div>
                    <span className="badge badge-secondary">
                      {content.source}
                    </span>
                  </div>
                </div>
              </div>
              
              <div className="flex items-center space-x-2">
                <span className={`badge ${getContentTypeColor(content.content_type)}`}>
                  {content.content_type}
                </span>
              </div>
            </div>

            {/* Summary */}
            {content.summary && (
              <p className="text-secondary-700 mb-4 line-clamp-3">
                {content.summary}
              </p>
            )}

            {/* Tags */}
            {content.tags && content.tags.length > 0 && (
              <div className="flex flex-wrap gap-2 mb-4">
                {content.tags.slice(0, 5).map((tag) => (
                  <span
                    key={tag.id}
                    className="badge badge-primary text-xs"
                  >
                    <Tag className="h-3 w-3 mr-1" />
                    {tag.name}
                  </span>
                ))}
                {content.tags.length > 5 && (
                  <span className="text-xs text-secondary-500">
                    +{content.tags.length - 5} more
                  </span>
                )}
              </div>
            )}

            {/* Actions */}
            <div className="flex items-center justify-between pt-4 border-t border-secondary-200">
              <div className="flex items-center space-x-2">
                <button
                  onClick={() => handleFeedback(content.id, 'like')}
                  disabled={interactingContent === content.id}
                  className="flex items-center space-x-1 px-3 py-1 rounded-md hover:bg-green-50 hover:text-green-700 transition-colors disabled:opacity-50"
                >
                  <ThumbsUp className="h-4 w-4" />
                  <span className="text-sm">Like</span>
                </button>
                
                <button
                  onClick={() => handleFeedback(content.id, 'dislike')}
                  disabled={interactingContent === content.id}
                  className="flex items-center space-x-1 px-3 py-1 rounded-md hover:bg-red-50 hover:text-red-700 transition-colors disabled:opacity-50"
                >
                  <ThumbsDown className="h-4 w-4" />
                  <span className="text-sm">Dislike</span>
                </button>
                
                <button
                  onClick={() => handleFeedback(content.id, 'share')}
                  disabled={interactingContent === content.id}
                  className="flex items-center space-x-1 px-3 py-1 rounded-md hover:bg-blue-50 hover:text-blue-700 transition-colors disabled:opacity-50"
                >
                  <Share2 className="h-4 w-4" />
                  <span className="text-sm">Share</span>
                </button>
                
                <button
                  onClick={() => handleFeedback(content.id, 'view')}
                  disabled={interactingContent === content.id}
                  className="flex items-center space-x-1 px-3 py-1 rounded-md hover:bg-purple-50 hover:text-purple-700 transition-colors disabled:opacity-50"
                >
                  <Bookmark className="h-4 w-4" />
                  <span className="text-sm">Save</span>
                </button>
              </div>
              
              <a
                href={content.url}
                target="_blank"
                rel="noopener noreferrer"
                className="btn-primary text-sm"
              >
                <ExternalLink className="h-4 w-4 mr-1" />
                Read
              </a>
            </div>
          </motion.div>
        ))}
      </AnimatePresence>
    </div>
  );
} 