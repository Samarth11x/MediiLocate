import React from 'react';

/**
 * BrandMark - MediLocate AI Brand Emblem
 * Combines a location marker with a healthcare cross in the approved brand palette.
 */
export default function BrandMark({ size = 'md', className = '' }) {
  const sizeMap = {
    sm: 28,
    md: 36,
    lg: 56,
  };

  const dimension = sizeMap[size] || 36;

  return (
    <span className={`brand-mark brand-mark--${size} ${className}`} aria-hidden="true">
      <svg
        width={dimension}
        height={dimension}
        viewBox="0 0 64 64"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
      >
        <rect width="64" height="64" rx="14" fill="#0F766E" />
        <path
          d="M32 10C22.611 10 15 17.611 15 27c0 12.5 17 27 17 27s17-14.5 17-27c0-9.389-7.611-17-17-17z"
          fill="#123047"
        />
        <circle cx="32" cy="27" r="11" fill="#D1FAE5" />
        <path
          d="M32 20v14M25 27h14"
          stroke="#0F766E"
          strokeWidth="3.5"
          strokeLinecap="round"
        />
      </svg>
    </span>
  );
}
