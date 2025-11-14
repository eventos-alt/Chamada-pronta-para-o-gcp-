import React from 'react';
import { Card, CardContent, CardHeader } from './ui/card';

const SkeletonLoader = ({ type = 'cards', count = 4 }) => {
  if (type === 'cards') {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {Array.from({ length: count }).map((_, index) => (
          <Card key={index} className="animate-pulse">
            <CardHeader className="space-y-2">
              <div className="flex items-center justify-between">
                <div className="h-4 w-24 bg-gray-200 dark:bg-gray-700 rounded skeleton"></div>
                <div className="h-8 w-8 bg-gray-200 dark:bg-gray-700 rounded-full skeleton"></div>
              </div>
            </CardHeader>
            <CardContent>
              <div className="h-8 w-16 bg-gray-200 dark:bg-gray-700 rounded skeleton mb-2"></div>
              <div className="h-3 w-32 bg-gray-200 dark:bg-gray-700 rounded skeleton"></div>
            </CardContent>
          </Card>
        ))}
      </div>
    );
  }

  if (type === 'chart') {
    return (
      <Card className="animate-pulse">
        <CardHeader>
          <div className="h-5 w-48 bg-gray-200 dark:bg-gray-700 rounded skeleton"></div>
        </CardHeader>
        <CardContent>
          <div className="h-64 bg-gray-200 dark:bg-gray-700 rounded skeleton"></div>
        </CardContent>
      </Card>
    );
  }

  if (type === 'table') {
    return (
      <Card className="animate-pulse">
        <CardHeader>
          <div className="h-5 w-32 bg-gray-200 dark:bg-gray-700 rounded skeleton"></div>
        </CardHeader>
        <CardContent className="space-y-3">
          {Array.from({ length: count }).map((_, index) => (
            <div key={index} className="flex items-center space-x-4">
              <div className="h-10 w-10 bg-gray-200 dark:bg-gray-700 rounded-full skeleton"></div>
              <div className="flex-1 space-y-2">
                <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded skeleton"></div>
                <div className="h-3 w-3/4 bg-gray-200 dark:bg-gray-700 rounded skeleton"></div>
              </div>
            </div>
          ))}
        </CardContent>
      </Card>
    );
  }

  if (type === 'insights') {
    return (
      <Card className="animate-pulse">
        <CardHeader className="space-y-2">
          <div className="h-5 w-64 bg-gray-200 dark:bg-gray-700 rounded skeleton"></div>
        </CardHeader>
        <CardContent className="space-y-4">
          {Array.from({ length: count }).map((_, index) => (
            <div key={index} className="bg-gray-50 dark:bg-gray-800 rounded-lg p-4 space-y-2">
              <div className="h-4 w-full bg-gray-200 dark:bg-gray-700 rounded skeleton"></div>
              <div className="h-3 w-5/6 bg-gray-200 dark:bg-gray-700 rounded skeleton"></div>
            </div>
          ))}
        </CardContent>
      </Card>
    );
  }

  return null;
};

export default SkeletonLoader;