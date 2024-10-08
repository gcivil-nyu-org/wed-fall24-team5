/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    /**
         * HTML. Paths to Django template files that will contain Tailwind CSS classes.
         */

    /*  Templates in src (src/templates), e.g. base.html. */
    './templates/**/*.html',

    /* Templates in other django apps (src/<any_app_name>/templates). */
    './**/templates/**/*.html',

  ],
  theme: {
    extend: {},
  },
  plugins: [
    require('@tailwindcss/forms'),
  ],
}

