project('welcome',
          version: '0.1.0',
    meson_version: '>= 0.62.0',
  default_options: [ 'warning_level=2', 'werror=false', ],
)

gnome = import('gnome')
i18n = import('i18n')

install_data('welcome.py', install_dir: join_paths(get_option('datadir'), 'radxa-welcome'))
install_data('welcome_support.py', install_dir: join_paths(get_option('datadir'), 'radxa-welcome'))
install_data('launch.py', install_dir: join_paths(get_option('datadir'), 'radxa-welcome'))
install_data('radxa-welcome', install_dir: join_paths(get_option('bindir')))

subdir('po')
subdir('data')


