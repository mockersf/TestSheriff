class python-modules {
  package { ['pymongo', 'flask', 'flask-restful']:
    ensure => present,
    provider => pip,
  }
  package { ['pytest', 'pytest-cov']:
    ensure => present,
    provider => pip,
  }
}
