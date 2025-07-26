import React, { useState, useEffect } from 'react';
import { Search, Download, Heart, User, ExternalLink } from 'lucide-react';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Card, CardContent } from '../components/ui/card';

interface ImageData {
  id: string;
  description: string;
  urls: {
    small: string;
    regular: string;
    full: string;
  };
  user: {
    name: string;
    username: string;
    profile_url?: string;
  };
  likes: number;
  color: string;
  tags: string[];
  download_url?: string;
}

interface APIResponse {
  success: boolean;
  data: ImageData[];
  message: string;
}

const ImageSearch: React.FC = () => {
  const [query, setQuery] = useState('coffee shop');
  const [images, setImages] = useState<ImageData[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const searchImages = async (searchQuery: string) => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await fetch(
        `http://127.0.0.1:8000/api/images/search?query=${encodeURIComponent(searchQuery)}&per_page=6`
      );
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data: APIResponse = await response.json();
      
      if (data.success) {
        setImages(data.data);
      } else {
        setError('Failed to fetch images');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch images');
      console.error('Error fetching images:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (query.trim()) {
      searchImages(query.trim());
    }
  };

  const loadCuratedImages = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await fetch('http://127.0.0.1:8000/api/images/curated?per_page=6');
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data: APIResponse = await response.json();
      
      if (data.success) {
        setImages(data.data);
        setQuery('Curated Images');
      } else {
        setError('Failed to fetch curated images');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch curated images');
      console.error('Error fetching curated images:', err);
    } finally {
      setLoading(false);
    }
  };

  // Load initial images
  useEffect(() => {
    searchImages('coffee shop');
  }, []);

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 via-white to-blue-50">
      <div className="container mx-auto px-4 py-8">
        <div className="max-w-6xl mx-auto">
          {/* Header */}
          <div className="text-center mb-8">
            <h1 className="text-4xl font-bold text-gray-900 mb-4">
              Image Search Gallery
            </h1>
            <p className="text-lg text-gray-600 mb-6">
              Discover beautiful images powered by Unsplash API
            </p>
          </div>

          {/* Search Form */}
          <div className="mb-8">
            <form onSubmit={handleSearch} className="flex gap-4 max-w-2xl mx-auto">
              <div className="relative flex-1">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
                <Input
                  type="text"
                  placeholder="Search for images..."
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  className="pl-10 h-12 text-lg"
                />
              </div>
              <Button 
                type="submit" 
                disabled={loading}
                className="h-12 px-8 bg-purple-600 hover:bg-purple-700"
              >
                {loading ? 'Searching...' : 'Search'}
              </Button>
            </form>
            
            <div className="text-center mt-4">
              <Button
                variant="outline"
                onClick={loadCuratedImages}
                disabled={loading}
                className="bg-blue-50 hover:bg-blue-100 border-blue-200"
              >
                Load Curated Images
              </Button>
            </div>
          </div>

          {/* Error Message */}
          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg mb-6 max-w-2xl mx-auto">
              <p className="font-medium">Error: {error}</p>
              <p className="text-sm mt-1">Make sure the backend server is running on 127.0.0.1:8000</p>
            </div>
          )}

          {/* Loading State */}
          {loading && (
            <div className="text-center py-12">
              <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600"></div>
              <p className="mt-4 text-gray-600">Searching for amazing images...</p>
            </div>
          )}

          {/* Images Grid */}
          {!loading && images.length > 0 && (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {images.map((image) => (
                <Card key={image.id} className="group hover:shadow-xl transition-all duration-300 transform hover:-translate-y-1">
                  <CardContent className="p-0">
                    <div className="relative overflow-hidden rounded-t-lg">
                      <img
                        src={image.urls.regular}
                        alt={image.description || 'Unsplash image'}
                        className="w-full h-64 object-cover group-hover:scale-105 transition-transform duration-300"
                        loading="lazy"
                      />
                      <div className="absolute inset-0 bg-black bg-opacity-0 group-hover:bg-opacity-20 transition-all duration-300 flex items-center justify-center">
                        <div className="opacity-0 group-hover:opacity-100 transition-opacity duration-300 flex gap-2">
                          <Button
                            size="sm"
                            variant="secondary"
                            className="bg-white bg-opacity-90 hover:bg-opacity-100"
                            onClick={() => window.open(image.urls.full, '_blank')}
                          >
                            <ExternalLink className="w-4 h-4" />
                          </Button>
                          {image.download_url && (
                            <Button
                              size="sm"
                              variant="secondary"
                              className="bg-white bg-opacity-90 hover:bg-opacity-100"
                              onClick={() => window.open(image.download_url, '_blank')}
                            >
                              <Download className="w-4 h-4" />
                            </Button>
                          )}
                        </div>
                      </div>
                    </div>
                    
                    <div className="p-4">
                      <h3 className="font-semibold text-gray-900 mb-2 line-clamp-2">
                        {image.description || 'Beautiful image from Unsplash'}
                      </h3>
                      
                      <div className="flex items-center justify-between text-sm text-gray-600 mb-3">
                        <div className="flex items-center gap-2">
                          <User className="w-4 h-4" />
                          <span className="truncate">
                            {image.user.name || image.user.username}
                          </span>
                        </div>
                        <div className="flex items-center gap-1">
                          <Heart className="w-4 h-4 text-red-500" />
                          <span>{image.likes.toLocaleString()}</span>
                        </div>
                      </div>
                      
                      {image.tags && image.tags.length > 0 && (
                        <div className="flex flex-wrap gap-1">
                          {image.tags.slice(0, 3).map((tag, index) => (
                            <span
                              key={index}
                              className="px-2 py-1 bg-gray-100 text-gray-700 text-xs rounded-full"
                            >
                              {tag}
                            </span>
                          ))}
                        </div>
                      )}
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}

          {/* No Results */}
          {!loading && images.length === 0 && !error && (
            <div className="text-center py-12">
              <div className="w-24 h-24 mx-auto mb-4 bg-gray-100 rounded-full flex items-center justify-center">
                <Search className="w-12 h-12 text-gray-400" />
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-2">No images found</h3>
              <p className="text-gray-600">Try searching for something else or load curated images</p>
            </div>
          )}

          {/* Footer */}
          <div className="text-center mt-12 pt-8 border-t border-gray-200">
            <p className="text-gray-600">
              Images provided by{' '}
              <a
                href="https://unsplash.com"
                target="_blank"
                rel="noopener noreferrer"
                className="text-purple-600 hover:text-purple-700 font-medium"
              >
                Unsplash
              </a>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ImageSearch;