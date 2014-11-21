class python-modules {
  package { ['pymongo', 'flask']:
    ensure => present,
    provider => pip,
  }
  package { ['pytest', 'pytest-cov']:
    ensure => present,
    provider => pip,
  }
}
