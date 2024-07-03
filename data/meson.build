gnome.compile_resources(
  'com.radxa.welcome',
  'com.radxa.welcome.gresource.xml',
  gresource_bundle: true,
  source_dir: meson.current_build_dir(),
  install_dir: join_paths(get_option('datadir'), 'radxa-welcome/data'),
  install: true
)


desktop_file = i18n.merge_file(
        input: 'com.radxa.welcome.desktop.in',
       output: 'com.radxa.welcome.desktop',
         type: 'desktop',
       po_dir: '../po',
      install: true,
  install_dir: join_paths(get_option('datadir'), 'applications')
)

desktop_utils = find_program('desktop-file-validate', required: false)
if desktop_utils.found()
  test('Validate desktop file', desktop_utils, args: [desktop_file], should_fail: false)
endif

appstream_file = i18n.merge_file(
        input: 'com.radxa.welcome.appdata.xml.in',
       output: 'com.radxa.welcome.appdata.xml',
       po_dir: '../po',
      install: true,
  install_dir: join_paths(get_option('datadir'), 'metainfo')
)

appstream_util = find_program('appstream-util', required: false)
if appstream_util.found()
  test('Validate appstream file', appstream_util, args: ['validate', appstream_file], should_fail: true)
endif

install_data('com.radxa.welcome.gschema.xml',
  install_dir: join_paths(get_option('datadir'), 'glib-2.0/schemas')
)

compile_schemas = find_program('glib-compile-schemas', required: false)
if compile_schemas.found()
  test('Validate schema file',
       compile_schemas,
       args: ['--strict', '--dry-run', meson.current_source_dir()])
endif

install_data('ui/window.ui',
  install_dir: join_paths(get_option('datadir'), 'radxa-welcome/data/ui')
)
install_data('ui/preferences.ui',
  install_dir: join_paths(get_option('datadir'), 'radxa-welcome/data/ui')
)
install_data('ui/apps_page.ui',
  install_dir: join_paths(get_option('datadir'), 'radxa-welcome/data/ui')
)
install_data('ui/links_page.ui',
  install_dir: join_paths(get_option('datadir'), 'radxa-welcome/data/ui')
)
install_data('ui/main.css',
  install_dir: join_paths(get_option('datadir'), 'radxa-welcome/data/ui')
)

install_data('settings/settings.json',
  install_dir: join_paths(get_option('datadir'), 'radxa-welcome/data/settings')
)

subdir('icons')
subdir('assets')