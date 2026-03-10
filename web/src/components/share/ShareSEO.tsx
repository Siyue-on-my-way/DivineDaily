import { useEffect } from 'react';

interface ShareSEOProps {
  title: string;
  description: string;
  url: string;
  imageUrl?: string;
}

export function ShareSEO({ title, description, url, imageUrl }: ShareSEOProps) {
  const defaultImage = 'https://divinedaily.com/og-image.png'; // 替换为实际图片URL
  const image = imageUrl || defaultImage;

  useEffect(() => {
    // Update document title
    document.title = `${title} - DivineDaily`;

    // Update or create meta tags
    const updateMetaTag = (property: string, content: string, isProperty = true) => {
      const attribute = isProperty ? 'property' : 'name';
      let element = document.querySelector(`meta[${attribute}="${property}"]`);
      
      if (!element) {
        element = document.createElement('meta');
        element.setAttribute(attribute, property);
        document.head.appendChild(element);
      }
      
      element.setAttribute('content', content);
    };

    // Basic Meta Tags
    updateMetaTag('description', description, false);
    
    // Open Graph / Facebook
    updateMetaTag('og:type', 'website');
    updateMetaTag('og:url', url);
    updateMetaTag('og:title', `${title} - DivineDaily`);
    updateMetaTag('og:description', description);
    updateMetaTag('og:image', image);
    updateMetaTag('og:image:width', '1200');
    updateMetaTag('og:image:height', '630');
    updateMetaTag('og:site_name', 'DivineDaily');
    updateMetaTag('og:locale', 'zh_CN');
    
    // Twitter Card
    updateMetaTag('twitter:card', 'summary_large_image', false);
    updateMetaTag('twitter:url', url, false);
    updateMetaTag('twitter:title', `${title} - DivineDaily`, false);
    updateMetaTag('twitter:description', description, false);
    updateMetaTag('twitter:image', image, false);
    
    // Additional Meta Tags
    updateMetaTag('robots', 'index, follow', false);

    // Update canonical link
    let canonical = document.querySelector('link[rel="canonical"]') as HTMLLinkElement;
    if (!canonical) {
      canonical = document.createElement('link');
      canonical.rel = 'canonical';
      document.head.appendChild(canonical);
    }
    canonical.href = url;

  }, [title, description, url, image]);

  return null;
}

