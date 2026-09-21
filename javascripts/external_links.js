document$.subscribe(function () {
  if (
    (window.location.hostname === 'mas.owasp.org' || window.location.hostname === 'localhost') &&
    (window.location.pathname.startsWith('/MASTG') || window.location.pathname.startsWith('/MASVS'))
  ) {
    const links = document.links;

    for (let i = 0; i < links.length; i++) {
      const link = links[i];

      // Exclude links to mas.owasp.org
      if (link.hostname === 'mas.owasp.org') {
        continue; // Skip this link
      }

      // Exclude links that match any of the excluded substrings
      const excludedSubstrings = [
        'github.com/OWASP',
        'raw.githubusercontent.com/OWASP',
        'github.com/cpholguera',
        'infosec.exchange/@OWASP_MAS',
        'bsky.app/profile/owasp-mas.bsky.social',
        'owasp.slack.com',
        'mailto:'
      ];
      if (excludedSubstrings.some(sub => link.href.includes(sub))) {
        continue; // Skip this link
      }

      // Exclude links that are images (have only an <img> inside)
      if (link.children.length === 1 && link.children[0].tagName === 'IMG') {
        continue; // Skip image-only links
      }

      if (link.hostname !== window.location.hostname) {
        link.setAttribute('target', '_blank');

        // Create an icon element (e.g., a small arrow)
        const icon = document.createElement('span');
        icon.textContent = ' ↗';

        // Append the icon to the link
        link.appendChild(icon);
      }
    }
  }
})
