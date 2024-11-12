module.exports = {
  testEnvironment: 'jsdom',
  testMatch: [
    '**/static/js/**/*.test.js'
  ],
  moduleDirectories: ['node_modules'],
  transform: {
    '^.+\\.js$': 'babel-jest'
  }
}; 