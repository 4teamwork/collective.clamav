Changelog
=========

2.0a3 (unreleased)
------------------

- Add Plone 4.3 compatability. [djowett-ftw]
- Add a setting to disable virus scanning (Defaults to true). [djowett-ftw]
- Use a previous scan result from the same request whether or not it passed
  [djowett-ftw]
- Add tests for AT validator [djowett-ftw]
- Cache scan results using annotations on the request [djowett-ftw]
- Add a 'scanStream' method to IValidator / ClamavValidator
  and use it in validators (this saves memory doing scans) [djowett-ftw]
- Copy new logic for archetypes validator to z3cform validator so tests pass
  (not tested manually) [djowett-ftw]
- Add logging of scan results to separate 'collective.clamav.log' (rotating)
  logfile.  [djowett-ftw]
- Setup translations, and translate some error messages to German.
  [djowett-ftw]


2.0a2 (2016-09-12)
------------------

- Fix ReST/pypi page syntax.
  [timo]


2.0a1 (2016-09-12)
------------------

- Initial release based on collective.ATClamAV with a new controlpanel module
  and and a configuration configlet for Plone 5 compatibility. The product
  and release works with Dexterity content types. [andreasma]

- Complete Plone 5 compatibility and transferring and adapting tests from
  collective.ATClamAV.
  [sneridagh]
