module.exports = {
  parserPreset: {
    parserOpts: {
      headerPattern: /^(\w+)(?:\(([^)]+)\))?(!)?: (.+)$/,
      headerCorrespondence: ['type', 'scope', 'breaking', 'subject']
    }
  },
  rules: {
    'header-max-length': [2, 'always', 100],
    'type-empty': [2, 'never'],
    'type-enum': [
      2,
      'always',
      ['feat', 'fix', 'docs', 'style', 'refactor', 'perf', 'test', 'build', 'ci', 'chore', 'revert']
    ],
    'scope-case': [2, 'always', 'kebab-case'],
    'subject-empty': [2, 'never'],
    'subject-full-stop': [2, 'never', '.']
  }
}
