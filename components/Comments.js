'use client';

import { useState, useEffect } from 'react';

export default function Comments({ songSlug, songTitle }) {
  const [comments, setComments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [name, setName] = useState('');
  const [comment, setComment] = useState('');
  const [rating, setRating] = useState(5);
  const [submitting, setSubmitting] = useState(false);
  const [success, setSuccess] = useState(false);

  useEffect(() => {
    fetchComments();
  }, [songSlug]);

  const fetchComments = async () => {
    try {
      const res = await fetch(`/api/comments?slug=${songSlug}`);
      const data = await res.json();
      setComments(data.comments || []);
    } catch (e) {
      console.error('Failed to fetch comments');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!name.trim() || !comment.trim()) return;

    setSubmitting(true);
    try {
      const res = await fetch('/api/comments', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ songSlug, name: name.trim(), comment: comment.trim(), rating }),
      });

      if (res.ok) {
        setSuccess(true);
        setName('');
        setComment('');
        setRating(5);
        fetchComments();
        setTimeout(() => setSuccess(false), 3000);
      }
    } catch (e) {
      console.error('Failed to post comment');
    } finally {
      setSubmitting(false);
    }
  };

  const formatDate = (dateStr) => {
    const d = new Date(dateStr);
    return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
  };

  return (
    <div className="mt-8 bg-gray-900/50 border border-gray-700/50 rounded-xl p-6">
      <h3 className="text-xl font-bold text-orange-400 mb-4">💬 Comments & Ratings</h3>

      {/* Submit Form */}
      <form onSubmit={handleSubmit} className="mb-6 space-y-3">
        <div className="flex gap-3">
          <input
            type="text"
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="Your name"
            maxLength={50}
            className="flex-1 px-3 py-2 bg-gray-800 border border-gray-600 rounded-lg text-white text-sm placeholder:text-gray-500 focus:outline-none focus:border-orange-500"
          />
          <div className="flex items-center gap-1">
            {[1, 2, 3, 4, 5].map(star => (
              <button
                key={star}
                type="button"
                onClick={() => setRating(star)}
                className={`text-xl ${star <= rating ? 'text-yellow-400' : 'text-gray-600'} hover:text-yellow-300`}
              >
                ★
              </button>
            ))}
          </div>
        </div>
        <textarea
          value={comment}
          onChange={(e) => setComment(e.target.value)}
          placeholder={`Share your experience learning ${songTitle}...`}
          maxLength={500}
          rows={3}
          className="w-full px-3 py-2 bg-gray-800 border border-gray-600 rounded-lg text-white text-sm placeholder:text-gray-500 focus:outline-none focus:border-orange-500 resize-none"
        />
        <div className="flex justify-between items-center">
          <span className="text-xs text-gray-500">{comment.length}/500</span>
          <button
            type="submit"
            disabled={submitting || !name.trim() || !comment.trim()}
            className="px-4 py-2 bg-orange-600 hover:bg-orange-500 disabled:bg-gray-600 disabled:cursor-not-allowed text-white text-sm font-bold rounded-lg transition-colors"
          >
            {submitting ? 'Posting...' : 'Post Comment'}
          </button>
        </div>
        {success && <p className="text-green-400 text-sm">✓ Comment posted!</p>}
      </form>

      {/* Comments List */}
      {loading ? (
        <p className="text-gray-500 text-sm">Loading comments...</p>
      ) : comments.length === 0 ? (
        <p className="text-gray-500 text-sm text-center py-4">No comments yet. Be the first to share your experience!</p>
      ) : (
        <div className="space-y-4">
          {comments.map((c) => (
            <div key={c.id || c._id} className="border-t border-gray-700/50 pt-4">
              <div className="flex items-center justify-between mb-1">
                <div className="flex items-center gap-2">
                  <span className="font-semibold text-sm text-orange-300">{c.name}</span>
                  <span className="text-yellow-400 text-xs">{'★'.repeat(c.rating)}{'☆'.repeat(5 - c.rating)}</span>
                </div>
                <span className="text-xs text-gray-500">{formatDate(c.createdAt)}</span>
              </div>
              <p className="text-gray-300 text-sm">{c.comment}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
