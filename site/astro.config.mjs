import { defineConfig } from 'astro/config';
import starlight from '@astrojs/starlight';

export default defineConfig({
  site: 'https://mlorentedev.github.io',
  base: '/youtube-toolkit',
  integrations: [
    starlight({
      title: 'YouTube Toolkit',
      social: [
        {
          icon: 'github',
          label: 'GitHub',
          href: 'https://github.com/mlorentedev/youtube-toolkit',
        },
      ],
      sidebar: [
        {
          label: 'Guides',
          items: [{ label: 'Getting Started', slug: 'getting-started' }],
        },
      ],
    }),
  ],
});
