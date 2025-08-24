module.exports = {
  testEnvironment: 'jsdom',
  setupFilesAfterEnv: ['<rootDir>/stircraft/stir_craft/tests/test_javascript_setup.js'],
  testMatch: [
    '<rootDir>/stircraft/stir_craft/tests/*.test.js'
  ],
  collectCoverageFrom: [
    'stircraft/staticfiles/js/**/*.js',
    '!**/node_modules/**'
  ],
  verbose: true
};
