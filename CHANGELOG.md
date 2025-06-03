# CHANGELOG


## v2.8.17 (2025-06-03)

### Bug Fixes

- Properly bundle static_viewer.html
  ([`89df689`](https://github.com/Kitware/trame-vtk/commit/89df689f124f7b08835efdfed4216c347d84c391))


## v2.8.16 (2025-06-02)

### Bug Fixes

- Skip bundling tests and examples
  ([`ad46ed4`](https://github.com/Kitware/trame-vtk/commit/ad46ed4e488e167fd2bcce0dc17bf187ba8b6cfd))

- **LICENSE**: Update sym link
  ([`9ccf71c`](https://github.com/Kitware/trame-vtk/commit/9ccf71c0fe4855d4f16c70454331e309968baa85))

### Continuous Integration

- Fix fetch/check scripts
  ([`fe6a0e0`](https://github.com/Kitware/trame-vtk/commit/fe6a0e041f6b2a36b31b907ba1d70a8c7ee3fef2))

- Update path
  ([`15bc970`](https://github.com/Kitware/trame-vtk/commit/15bc970ee60e21434d8db97b6fadacad24ce2b4c))

### Documentation

- Update links in readme
  ([`f73f046`](https://github.com/Kitware/trame-vtk/commit/f73f0465a9fd9989c07244ae666429e68b97cd53))


## v2.8.15 (2025-02-09)

### Bug Fixes

- **vtk**: Add support for multiple views using ParaView protocol as ref
  ([`02a5568`](https://github.com/Kitware/trame-vtk/commit/02a5568a113421a3da2a7c64634bfcb4be1c837c))

### Continuous Integration

- Install osmesa
  ([`97a02e5`](https://github.com/Kitware/trame-vtk/commit/97a02e5a6a165b56ff4e45110d6bd0e6223175aa))

- Try to fix testing
  ([`242da1e`](https://github.com/Kitware/trame-vtk/commit/242da1ef544d8a0368b07cc0fa33ffbf86ff239d))

- Update .codespellrc to skip changelog
  ([`166e50c`](https://github.com/Kitware/trame-vtk/commit/166e50c0f778a209324dd5da334549ff1013f894))

- Update upload artifact
  ([`bada39f`](https://github.com/Kitware/trame-vtk/commit/bada39f4a19540d642f69b442e2c62bf61a5e8b7))

### Documentation

- **js**: List JS dependency
  ([`e2e3a43`](https://github.com/Kitware/trame-vtk/commit/e2e3a43fc32a0748b97338872c23fa495c9a89d1))

- **readme**: Fix typo
  ([`990ad17`](https://github.com/Kitware/trame-vtk/commit/990ad17a419aee0630cf8de93b567fa092f588f8))

### Testing

- Cover several vtk version
  ([`274da78`](https://github.com/Kitware/trame-vtk/commit/274da788bcfa15abf4f453158e14ad5210895e2f))


## v2.8.14 (2025-01-08)

### Bug Fixes

- **server**: Skip call on protocol if not present
  ([`19e2394`](https://github.com/Kitware/trame-vtk/commit/19e2394cee986040c3aa93f05c6ac14525217c38))

### Continuous Integration

- Use pyproject and ruff
  ([`290cd3e`](https://github.com/Kitware/trame-vtk/commit/290cd3e1afcf0e5e69a4f4eeea6023ee5028febb))

- **pre-commit**: Fix codespell
  ([`df46242`](https://github.com/Kitware/trame-vtk/commit/df46242bc34c9e89b9ed42445f77ddd16bb15720))


## v2.8.13 (2025-01-07)

### Bug Fixes

- **VtkLocalView**: Do not call helper.scene if no protocol
  ([`fa7571d`](https://github.com/Kitware/trame-vtk/commit/fa7571d4370180c34258db3cdf2388ff5803c210))

### Documentation

- Update README.rst
  ([`38ad9b2`](https://github.com/Kitware/trame-vtk/commit/38ad9b220a4674f5d820e0252302fc1688c80731))


## v2.8.12 (2024-11-08)

### Performance Improvements

- **vtk**: Do not always force image push
  ([`d2b075f`](https://github.com/Kitware/trame-vtk/commit/d2b075fa00958d2e8ebcad052db89a7a41d3ce4f))


## v2.8.11 (2024-10-17)

### Bug Fixes

- **animation**: Enable animation on remote view
  ([`660a1d4`](https://github.com/Kitware/trame-vtk/commit/660a1d4a755d43684a82f24efbfdb7bd445651cd))


## v2.8.10 (2024-08-07)

### Bug Fixes

- **wheel**: Apply modifiers [alt,shift,ctrl] on wheel event
  ([`42f2283`](https://github.com/Kitware/trame-vtk/commit/42f22838fe409d8b15ed158240ece25a46d0b7dc))


## v2.8.9 (2024-06-07)

### Bug Fixes

- **VtkView**: Add set_camera method
  ([`bc7e883`](https://github.com/Kitware/trame-vtk/commit/bc7e8833bbdc6b58d316c99586c04407be5a41d5))


## v2.8.8 (2024-05-06)

### Bug Fixes

- **js**: Track hash of vue-vtk-js as well
  ([`c82ffec`](https://github.com/Kitware/trame-vtk/commit/c82ffeca9d6d3bddbd65d630f3c6fc9864352eae))

Similar to offline_viewer.html we track and report mismatched hash of all external dependencies. see
  also https://github.com/Kitware/trame-vtk/pull/70

### Chores

- **js**: Allow triggering release on external artifact static_viewer.html
  ([`eb8461a`](https://github.com/Kitware/trame-vtk/commit/eb8461af4229588b71a8bd8f34bb72be162d877f))

Previously, when a new version of static_viewer.html is released on the master of vtk-js we couldn't
  trigger a release because we do not commit this file but rather grab it during release. This
  commit adds the hash of the latest version in a file and a hash check that runs during release but
  does not trigger a failure on a mismatch but rather a warning. So now if static_viewer.html is
  updated on vtk-js: - If we do not care `.fetch_externals.sh` will just emit a warning - If we
  **do** care we update .static_viewer.sha256 and trigger a new release on trame-vtk even if no
  other `trame-vtk` change happened during last release.


## v2.8.7 (2024-05-02)

### Bug Fixes

- **remote rendering**: Round view size half up
  ([`e6777b9`](https://github.com/Kitware/trame-vtk/commit/e6777b9161d381c01e9ec04f592093c9225f1adf))

comply with vue-vtk-js vtkRemoteView implementation which uses Math.round for setting view size.
  python builtin round function does not work the same way: it rounds half to even.


## v2.8.6 (2024-04-22)

### Bug Fixes

- **serializer**: Register vtkCompositePolyDataMapper
  ([`d8c55a8`](https://github.com/Kitware/trame-vtk/commit/d8c55a8be174d83b8b42a5ad3d1dfb379f3243a0))

### Documentation

- **readme**: Fix the link of tutorial url
  ([`0a46f97`](https://github.com/Kitware/trame-vtk/commit/0a46f97f951f0709a1547a7f4e169cf16c33324a))


## v2.8.5 (2024-02-15)

### Bug Fixes

- **py3.8**: Ensure compatibility across py version
  ([`36a58c1`](https://github.com/Kitware/trame-vtk/commit/36a58c14bd9320a1dfc4bb4e242feea5c48edac7))

* Fix breaks compatability with Python 3.8


## v2.8.4 (2024-02-14)

### Bug Fixes

- **serializer**: Md5 hashing is not allowed for FIPS
  ([`6e163d6`](https://github.com/Kitware/trame-vtk/commit/6e163d62199092d2e3dc2311e2b75f2572854790))


## v2.8.3 (2024-02-13)

### Bug Fixes

- **serializer**: Add encoding option
  ([`9c20a89`](https://github.com/Kitware/trame-vtk/commit/9c20a89297c356e8dd421ed5d47fb3ed03c660c7))


## v2.8.2 (2024-02-09)

### Bug Fixes

- **js**: Replace invalid downloaded js content
  ([`d45ca89`](https://github.com/Kitware/trame-vtk/commit/d45ca89ede99b50090c5dc70b6470abce26c126f))


## v2.8.1 (2024-02-09)

### Bug Fixes

- **dep**: Remove invalid vtk dep
  ([`7da4ffc`](https://github.com/Kitware/trame-vtk/commit/7da4ffcf5f31fed840a3d94edf0ae0afdaf534fd))

### Documentation

- **picking**: Finish remote example
  ([`1ebeadb`](https://github.com/Kitware/trame-vtk/commit/1ebeadbaaf0044f637f1aa969074c4a3f49570e0))


## v2.8.0 (2024-01-30)

### Bug Fixes

- **local**: Workaround for lut serializer
  ([`47bbda1`](https://github.com/Kitware/trame-vtk/commit/47bbda19702d1fdd1be4c815314b998f32719450))

### Features

- **picking**: Add support for picking modes
  ([`edab22d`](https://github.com/Kitware/trame-vtk/commit/edab22dfd6327be3d721efdfcb58a44de714c6c0))


## v2.7.1 (2024-01-26)

### Bug Fixes

- **local**: Add prop3d.orientation for local rendering
  ([`812c6d1`](https://github.com/Kitware/trame-vtk/commit/812c6d18a582b504f59c7e4dc1e60e2e4fb99b7f))


## v2.7.0 (2024-01-12)

### Continuous Integration

- Try to fix pytest execution
  ([`cc95261`](https://github.com/Kitware/trame-vtk/commit/cc952619090db59257637d964462d0fe16b81e3d))

### Documentation

- **widgets**: Provide info for LocalView and widgets
  ([`b467dc8`](https://github.com/Kitware/trame-vtk/commit/b467dc882062d4efde424384875f8a77bd5215c8))

### Features

- **multi-server**: Add support for multi-server
  ([`5a775ea`](https://github.com/Kitware/trame-vtk/commit/5a775ea8d0f3816f733ce9e9d68e0c798976bc64))


## v2.6.3 (2023-12-13)

### Bug Fixes

- **BigInt**: Convert points with (Big)Int to Float for LocalView
  ([`80496d5`](https://github.com/Kitware/trame-vtk/commit/80496d5ef38269a76e5f4a51c80e3340ad83d1d7))


## v2.6.2 (2023-11-16)

### Bug Fixes

- **ref**: Automatically assign non conflicting ref
  ([`3cfdf2a`](https://github.com/Kitware/trame-vtk/commit/3cfdf2ada97b1ccae04211e25e92744835621c2f))


## v2.6.1 (2023-11-13)

### Bug Fixes

- **protocol**: Allow several servers within 1 process
  ([`0c53288`](https://github.com/Kitware/trame-vtk/commit/0c53288add82f5aeea55d3b0190150580311a03b))


## v2.6.0 (2023-11-08)

### Bug Fixes

- Add `userMatrix` property to generic actor serializer
  ([`8eac87f`](https://github.com/Kitware/trame-vtk/commit/8eac87feddbd698bb48aecc1a47b500eb3a7ee1c))

- Remove missing `user_matrix`
  ([`491fcbd`](https://github.com/Kitware/trame-vtk/commit/491fcbdb9280d851912bdcfae0cda2cbf521141e))

### Features

- Add `userMatrix` property on generic volume serializer
  ([`33dfd36`](https://github.com/Kitware/trame-vtk/commit/33dfd367dc157e2b9df0aa93f92ff9b96dbfc9d2))

### Refactoring

- Pass `user_matrix` in `add_on` dictionary as payload to
  ([`ec6cfba`](https://github.com/Kitware/trame-vtk/commit/ec6cfbaaec1940dfc57fb990306f63cd1f56af0b))


## v2.5.10 (2023-11-07)

### Bug Fixes

- **vtk.js**: Bump vtk.js to 29.1.1
  ([`bd93a63`](https://github.com/Kitware/trame-vtk/commit/bd93a63907d2ff86fc67c247e751367f6e4753a0))


## v2.5.9 (2023-10-06)

### Bug Fixes

- **serializer**: Better handling of actor user matrix
  ([`9b5082a`](https://github.com/Kitware/trame-vtk/commit/9b5082a7fe86f215b5763f2270487c63a2e4d7d3))

- **serializer**: Remove unused import
  ([`5fe4da8`](https://github.com/Kitware/trame-vtk/commit/5fe4da8376f35d542bd4c621605b7504256203c8))

### Continuous Integration

- Update baseline with new pyvista
  ([`ba13822`](https://github.com/Kitware/trame-vtk/commit/ba138222831cc5f2c6ebddf519b50f722a6fd3fe))

- Update test baseline
  ([`8bf8b27`](https://github.com/Kitware/trame-vtk/commit/8bf8b27ac654f202896cb48b918af1a9bc388a32))

### Documentation

- **pyvista**: Add wip examples
  ([`487c4c0`](https://github.com/Kitware/trame-vtk/commit/487c4c03054c5a6dad3a671760d53a2375d3119f))


## v2.5.8 (2023-07-20)

### Bug Fixes

- **volume**: Use abs of sampleDistance
  ([`0bbb3ae`](https://github.com/Kitware/trame-vtk/commit/0bbb3ae772d1c0f2c916bedef93bc28cc0400dd3))

### Continuous Integration

- Add trame-vuetify as dep
  ([`c7259c0`](https://github.com/Kitware/trame-vtk/commit/c7259c05e502193f88fb19640b0388a465598380))


## v2.5.7 (2023-07-20)

### Bug Fixes

- Semantic-release version
  ([`4fd3148`](https://github.com/Kitware/trame-vtk/commit/4fd3148c9c513112cc445f14988864c1f9c8ae9f))

- **version**: Sync github and pypi
  ([`a783ca6`](https://github.com/Kitware/trame-vtk/commit/a783ca6b757f9192c18a951a8691c174952b9f53))

### Chores

- Update baseline .gitignore
  ([`bee0bf7`](https://github.com/Kitware/trame-vtk/commit/bee0bf7b3312de3895500d31d51303572d3c62db))

### Continuous Integration

- Ignore changelog for spelling
  ([`aafb2a4`](https://github.com/Kitware/trame-vtk/commit/aafb2a4681eff562324f724e2cbf5a49efab31b6))


## v2.5.6 (2023-07-19)

### Bug Fixes

- **VolumeRendering**: Add alias to support different mappers
  ([`cf540bc`](https://github.com/Kitware/trame-vtk/commit/cf540bc7472072ff9d8d379ca4905ee8b0fb82f2))

fix #46 fix #44

### Continuous Integration

- Changelog spelling
  ([`6d3b6f5`](https://github.com/Kitware/trame-vtk/commit/6d3b6f5c7acce73d81307f58091d64f9750311c0))

- **baseline**: Add ref baseline for volume
  ([`4ceb45c`](https://github.com/Kitware/trame-vtk/commit/4ceb45c968a51e0cc5482160bc3ded3de23db352))

- **baseline**: Add ref baselines
  ([`8b305e6`](https://github.com/Kitware/trame-vtk/commit/8b305e64550ed62a68db6589b0f6b9b9de386d07))

- **testing**: Rendering testing
  ([`70aeafa`](https://github.com/Kitware/trame-vtk/commit/70aeafa443617c2ac7e6f017769e6d7751d8a7b5))

fix #45


## v2.5.5 (2023-07-19)

### Bug Fixes

- **ParaView**: Push_image for different viewtypes
  ([`74ed533`](https://github.com/Kitware/trame-vtk/commit/74ed533a2a29930b2f33d0dd2fb77c30987a51e2))

Not using a RenderView as view for the vtkLocalRemoteView will crash, because
  "EnableRenderOnInteraction" might not be defined. "GetPropertyValue" will return None for a
  non-existing Property

### Chores

- **volume**: Add volume rendering example
  ([`672b1ad`](https://github.com/Kitware/trame-vtk/commit/672b1adb979bb865d3379bd6a947c8546d587022))

### Continuous Integration

- Upate baselines
  ([`68e1a2d`](https://github.com/Kitware/trame-vtk/commit/68e1a2db3a86742fa353d1032807459da57557e9))

- Upate baselines
  ([`082de9c`](https://github.com/Kitware/trame-vtk/commit/082de9c79f8a7b653bb5c71482e2bea97b050a49))


## v2.5.4 (2023-06-29)

### Bug Fixes

- **GC**: Allow to release view resources
  ([`bfe9c80`](https://github.com/Kitware/trame-vtk/commit/bfe9c8048b04fd41d72e150c009e33137a9e3e64))

### Continuous Integration

- Add gc testing
  ([`ef361f7`](https://github.com/Kitware/trame-vtk/commit/ef361f794728cf0b15c70f42c1e562d7cdcbcb6a))

- Add missing requirements
  ([`17407e3`](https://github.com/Kitware/trame-vtk/commit/17407e3f1edbfdca8dbdba37d15464e948567a58))

- Use better stage name
  ([`0bf3f73`](https://github.com/Kitware/trame-vtk/commit/0bf3f73b2257f2e49552d69ed2c5ad8f909e6487))


## v2.5.3 (2023-06-28)

### Bug Fixes

- **html**: Improve HTML exporting ([#42](https://github.com/Kitware/trame-vtk/pull/42),
  [`3a0184e`](https://github.com/Kitware/trame-vtk/commit/3a0184e86842f275d920827c3e1a5bb62f627655))


## v2.5.2 (2023-06-26)

### Bug Fixes

- **html**: Add tool for HTML export
  ([`3705560`](https://github.com/Kitware/trame-vtk/commit/3705560873ee0c9c4b846fe93568391a105d192d))

- **vue-vtk-js**: Update to pick lookuptable fix
  ([`1ecd65c`](https://github.com/Kitware/trame-vtk/commit/1ecd65cf9539b1dfec912e3d85560e0df794409b))

### Continuous Integration

- **testing**: Update baselines
  ([`d5b34a4`](https://github.com/Kitware/trame-vtk/commit/d5b34a4c06d977048e10d70c15cc4b482ba67efe))

- **testing**: Update baselines
  ([`0d6e494`](https://github.com/Kitware/trame-vtk/commit/0d6e4945f80ee56b7ecc8181d4341331989b7d0e))


## v2.5.1 (2023-06-23)

### Bug Fixes

- **LUT**: Do not discretize vtkColorTransferFunction with few control points
  ([`ebfaee4`](https://github.com/Kitware/trame-vtk/commit/ebfaee4f3abadb0e418beaa56d1de4e410425947))

### Continuous Integration

- Add browser testing
  ([`a804d55`](https://github.com/Kitware/trame-vtk/commit/a804d5516b7a57ea25807cf55b4b6bcaabdcdda4))

- Split steps
  ([`b1fdde6`](https://github.com/Kitware/trame-vtk/commit/b1fdde61d96681a9f052d4c75628367f1fe4069c))


## v2.5.0 (2023-06-16)

### Bug Fixes

- **local**: Keep vtkLookupTable as-is for vtk.js
  ([`a3b1904`](https://github.com/Kitware/trame-vtk/commit/a3b19046bf26e7e11a8d7d10063301b625cba2a0))

- **LookupTable**: Add support for color Table
  ([`46e3d6d`](https://github.com/Kitware/trame-vtk/commit/46e3d6d7ee05e4adcf7f664ae1e2f4ffe3188b7d))

- **vue-vtk-js**: Update vtk.js
  ([`96e569a`](https://github.com/Kitware/trame-vtk/commit/96e569ac37140baa643cfa14bf270c3fa388d2e2))

### Continuous Integration

- Add test baseline
  ([`5ad9763`](https://github.com/Kitware/trame-vtk/commit/5ad976321869b205543c12d52b4675dde5776be4))

- **black**: Run black
  ([`dfdc6fa`](https://github.com/Kitware/trame-vtk/commit/dfdc6fa6768a549362dbd3114beb7d08b94b18c7))

### Documentation

- **example**: Force reset camera in pyvista
  ([`d083796`](https://github.com/Kitware/trame-vtk/commit/d08379621902bc541e8f12a5e0716aa70f55249d))

- **validation**: Add lut preset example
  ([`3250926`](https://github.com/Kitware/trame-vtk/commit/3250926e6c050022cb28c6b60b95e18e2217c66f))

### Features

- **local**: Add caching with delta compute for local state
  ([`0d64fbb`](https://github.com/Kitware/trame-vtk/commit/0d64fbb836bec479c17045be57d4143734330aa3))

- **local**: Enable prop caching
  ([`be29552`](https://github.com/Kitware/trame-vtk/commit/be29552102b0394ae3e45bcc96a0c6b4f2af73dc))


## v2.4.4 (2023-04-16)

### Bug Fixes

- **export**: Handle fields for offline rendering
  ([`8b9920f`](https://github.com/Kitware/trame-vtk/commit/8b9920fdc7328d8fa20bd3d6c3d2566f1175d883))

- **ParaView**: Add missing widgets args in scene
  ([`47c4f0e`](https://github.com/Kitware/trame-vtk/commit/47c4f0efc3ad2feed4a12901a33e1442aab15b29))

### Documentation

- **pv**: Add paraview validation example
  ([`9146694`](https://github.com/Kitware/trame-vtk/commit/914669478cb2ba088131d8da81ddc287003afb23))


## v2.4.3 (2023-04-07)

### Bug Fixes

- **export**: Add export for VtkLocalView
  ([`b58ccf4`](https://github.com/Kitware/trame-vtk/commit/b58ccf4109b25f567cac0f8f1185ab71e00c14dc))


## v2.4.2 (2023-03-31)

### Bug Fixes

- **behavior**: Implement handler for vtkOrientationMarkerWidget
  ([`01e035f`](https://github.com/Kitware/trame-vtk/commit/01e035ff6f8f3fd52717b627f6db57961f4debc1))

- **LocalView**: Add infrastructure to support behaviors
  ([`26e1945`](https://github.com/Kitware/trame-vtk/commit/26e194535c2e5ca910ebc053b16bd7abacd91cbe))

- **VtkRemoteLocalView**: Add support for widgets
  ([`79d106a`](https://github.com/Kitware/trame-vtk/commit/79d106ac2ffb432517bef8f57d80551ff699466d))

- **vue-vtk-js**: Bump version of vue-vtk-js
  ([`11c14b9`](https://github.com/Kitware/trame-vtk/commit/11c14b9b19a6fe1d8019c63c2d94806caf438954))

Signed-off-by: Patrick Avery <patrick.avery@kitware.com>

- **widgets**: Use proper order initialization
  ([`f3c0505`](https://github.com/Kitware/trame-vtk/commit/f3c05053a81786fc1627cd55f5a360b580c52a10))

### Documentation

- **examples**: Add button toggles for widgets
  ([`ed307b3`](https://github.com/Kitware/trame-vtk/commit/ed307b32b888e9698e87f5f6af14b5f3cb2e4d8f))

- **examples**: Add pyvista axes widget examples
  ([`b1598f6`](https://github.com/Kitware/trame-vtk/commit/b1598f61c6a53d77acd5688026560069153e6886))

- **examples**: Simplify code
  ([`b9afcea`](https://github.com/Kitware/trame-vtk/commit/b9afceadd32a565aef380ec148a05d014e115687))

- **examples**: Update the widget ones
  ([`cdda471`](https://github.com/Kitware/trame-vtk/commit/cdda471df5c2364e7359c2d6533ffcd4e4b38cf0))


## v2.4.1 (2023-03-27)

### Bug Fixes

- **paraview**: Fix protocol
  ([`b72425c`](https://github.com/Kitware/trame-vtk/commit/b72425cdde30344b15cebf8dd1b11aa62701176f))


## v2.4.0 (2023-03-24)

### Bug Fixes

- **helper**: Update name to `_trame_server`
  ([`2b2b607`](https://github.com/Kitware/trame-vtk/commit/2b2b607da8abc3639b791c4411ffb22d9d3a147c))

This is the correct name

Signed-off-by: Patrick Avery <patrick.avery@kitware.com>

- **logger**: Add environment variable for setting serializer log level
  ([`3c1614c`](https://github.com/Kitware/trame-vtk/commit/3c1614c82f47528e71de69916baa22961177c3d9))

Now, only critical messages from serializers are printed by default, unless the
  `TRAME_SERIALIZE_DEBUG` environment variable is set, in which case all logger output will be
  printed from the serializers.

Signed-off-by: Patrick Avery <patrick.avery@kitware.com>

- **messages**: Only print no serializer warning once per instance type
  ([`65db322`](https://github.com/Kitware/trame-vtk/commit/65db3229b9b0d15183a3fa882a825b4a9ea745ea))

Signed-off-by: Patrick Avery <patrick.avery@kitware.com>

- **mouse_handler**: Apply a couple of fixes to mouse wheel event
  ([`45505ef`](https://github.com/Kitware/trame-vtk/commit/45505ef25bb76a4d04bddd9cecdc375999de9e1b))

First of all, this updates the interactor with the mouse position on a wheel event so that if there
  are multiple renderers, the interactor can figure out which one needs to be updated.

Second, this forwards the event to the interactor, rather than applying a manual zoom to the camera
  ourselves. This makes the behavior more consistent.

Third, this skips the zoom for the start event, since there appears to always be a wheel event right
  after it.

Fixes: pyvista/pyvista#4020

Signed-off-by: Patrick Avery <patrick.avery@kitware.com>

- **mouse_handler**: Only trigger animation registration on first "down"
  ([`88bac50`](https://github.com/Kitware/trame-vtk/commit/88bac500cbd3d6f3775a7cab9170c775a5683ff6))

This was copied over from the ParaView version of the mouse handler.

Signed-off-by: Patrick Avery <patrick.avery@kitware.com>

- **paraview**: Update mouse wheel to match VTK version
  ([`6f93186`](https://github.com/Kitware/trame-vtk/commit/6f931867e3b63aa59e03799495ade03c59b31abf))

Signed-off-by: Patrick Avery <patrick.avery@kitware.com>

- **vue-vtk-js**: Update vue-vtk-js to the newest version
  ([`eb7310d`](https://github.com/Kitware/trame-vtk/commit/eb7310dd9e763b069de438ad33db3173965c2e81))

This includes mouse position information for moving the mouse wheel, which we need.

Signed-off-by: Patrick Avery <patrick.avery@kitware.com>

- **vue-vtk-js**: Upgrade to prevent client error on unmount
  ([`3a2acee`](https://github.com/Kitware/trame-vtk/commit/3a2aceececd6f70e2bc4e78c309b051723eb9d45))

Signed-off-by: Patrick Avery <patrick.avery@kitware.com>

### Chores

- **checks**: Remove checks for wslink
  ([`5fea67d`](https://github.com/Kitware/trame-vtk/commit/5fea67d77d09f9f6468f63814c617d9d3e1f6786))

It is required and we don't need to check for its presence.

Signed-off-by: Patrick Avery <patrick.avery@kitware.com>

- **future**: Remove unneeded future imports
  ([`dd57968`](https://github.com/Kitware/trame-vtk/commit/dd579681599e658cc891f93f7494f97556d03de6))

Signed-off-by: Patrick Avery <patrick.avery@kitware.com>

### Code Style

- **formatting**: Fix flake8 and black issues
  ([`e69c80c`](https://github.com/Kitware/trame-vtk/commit/e69c80c64cce9b3cbd827a27efb743d5edf9e76f))

Signed-off-by: Patrick Avery <patrick.avery@kitware.com>

### Features

- **protocols**: Copy protocols from VTK exactly
  ([`9fe3c26`](https://github.com/Kitware/trame-vtk/commit/9fe3c261bc78a8814e1f4bab37ac6df3977144d8))

This copies the protocols and render_window_serializer from VTK exactly as they are. Further commits
  will modify the code.

Signed-off-by: Patrick Avery <patrick.avery@kitware.com>

### Refactoring

- **case**: Convert most variables from camelCase to snake_case
  ([`ba9beaf`](https://github.com/Kitware/trame-vtk/commit/ba9beaf5060ab2b992a85d7ae701f3f4853deba2))

I went through the code and automatically converted most of the variables from camelCase to
  snake_case using regex in vim. I skipped a couple of cases in particular:

1. Anything that started with `vtk` (this might be a VTK object) 2. Anything in quotes (since they
  might be strings sent to VTK.js)

There were, however, some things still that were modified that should not have been. I tried to
  manually fix these, but I may have not caught everything, so we should do testing to verify.

Signed-off-by: Patrick Avery <patrick.avery@kitware.com>

- **initializeSerializers()**: Reduce repetition
  ([`7e8b213`](https://github.com/Kitware/trame-vtk/commit/7e8b21332a3c4b3edd901047fb0568ec169012ed))

Signed-off-by: Patrick Avery <patrick.avery@kitware.com>

- **paraview**: Copy paraview protocols into repo
  ([`43fdc97`](https://github.com/Kitware/trame-vtk/commit/43fdc97989a16f5bf72b9d73ce7a591523acecf9))

This also splits them up into separate files.

Signed-off-by: Patrick Avery <patrick.avery@kitware.com>

- **paraview**: Fix import path for vtk_mesh
  ([`b3578a7`](https://github.com/Kitware/trame-vtk/commit/b3578a7d3b8aabb6ef0fa3b76c5280b3ba9e0c62))

Signed-off-by: Patrick Avery <patrick.avery@kitware.com>

- **protocols**: Break up protocols into separate files
  ([`7336447`](https://github.com/Kitware/trame-vtk/commit/73364475eb881b1752779ee558f1d87ad4a2f327))

Signed-off-by: Patrick Avery <patrick.avery@kitware.com>

- **protocols**: Remove unused protocols
  ([`d24e998`](https://github.com/Kitware/trame-vtk/commit/d24e9984d46b2bea194ea3e8a15a7208bfeba00c))

Signed-off-by: Patrick Avery <patrick.avery@kitware.com>

- **protocols**: Use local versions of protocols
  ([`315f06f`](https://github.com/Kitware/trame-vtk/commit/315f06fc99acf293c6dcbc6fc2457f1880cd07f1))

This appears to be working at least on a basic level.

Signed-off-by: Patrick Avery <patrick.avery@kitware.com>

- **pwf**: Move pwf serializer into lookup_tables
  ([`1ef8fd9`](https://github.com/Kitware/trame-vtk/commit/1ef8fd97682e262214e80dbde7889617c5a9c40c))

Signed-off-by: Patrick Avery <patrick.avery@kitware.com>

- **registry**: Remove unused context variable
  ([`5fd2640`](https://github.com/Kitware/trame-vtk/commit/5fd26407a1077874d7427c49407c7cf8d55bbb8e))

Signed-off-by: Patrick Avery <patrick.avery@kitware.com>

- **render_window_serializer**: Rename to serializers
  ([`1bec149`](https://github.com/Kitware/trame-vtk/commit/1bec1497279b1c95337bf9245ab7bfcccd730810))

This name fits better since it contains all kinds of serializers.

Signed-off-by: Patrick Avery <patrick.avery@kitware.com>

- **serialize**: Break up serializers into separate files
  ([`57d5f0d`](https://github.com/Kitware/trame-vtk/commit/57d5f0debab099e5918fed00e1c66c9556bd22b6))

Signed-off-by: Patrick Avery <patrick.avery@kitware.com>

- **serializers**: Apply patches from addon_serializer
  ([`a93a540`](https://github.com/Kitware/trame-vtk/commit/a93a5400f542c529024e18941f9323c7623cea12))

This takes the patches being applied in addon_serializer.py and puts them directly in the render
  window serializer. We should verify that there are no issues. But I did notice some discrepancies:

1. I saw no difference in `extractRequiredFields()` 2. The addon serializer did not call
  `registerInstanceSerializer()` on `vtkStructuredPoints` with the modified `imagedataSerializer`
  (only difference is that extent is used instead of dimensions). 3. The addon serializer did not
  call `registerInstanceSerializer()` on `vtkColorTransferFunction` with the modified
  `colorTransferFunctionSerializer`. 4. `genericMapperSerializer()` only had debug message
  modifications

Signed-off-by: Patrick Avery <patrick.avery@kitware.com>

- **serializers**: Move into subdirectory
  ([`114a83b`](https://github.com/Kitware/trame-vtk/commit/114a83b5ac4265a9d989b85ef0e389367fc10b76))

The file will be broken apart soon as well.

Signed-off-by: Patrick Avery <patrick.avery@kitware.com>

- **serializers**: Move one directory up
  ([`bd6c3da`](https://github.com/Kitware/trame-vtk/commit/bd6c3da1caf27837a7691ce95437155970473692))

It should be a sibling of the protocols, not a child.

Signed-off-by: Patrick Avery <patrick.avery@kitware.com>

- **updateZoomFromWheel**: Remove duplicated code
  ([`c9c07da`](https://github.com/Kitware/trame-vtk/commit/c9c07da41b71ecfbd6afa65db7ceeaf0609c5572))

Signed-off-by: Patrick Avery <patrick.avery@kitware.com>

- **utils**: Copy utils from vtk web
  ([`d338893`](https://github.com/Kitware/trame-vtk/commit/d338893528675ba17d24ed9c386ec27cfac67656))

This is one less dependency we need from vtkmodules.web

Signed-off-by: Patrick Avery <patrick.avery@kitware.com>

- **web**: Remove last use of vtkmodules.web
  ([`fcef60a`](https://github.com/Kitware/trame-vtk/commit/fcef60a42f19dac24bdede46ccda98758b75b8eb))

The functions being used were copied over.

Signed-off-by: Patrick Avery <patrick.avery@kitware.com>


## v2.3.5 (2023-03-21)

### Bug Fixes

- Axes serializer
  ([`cc2136d`](https://github.com/Kitware/trame-vtk/commit/cc2136df0d4ff850f25f791ffc76f3ae2ba10a92))


## v2.3.4 (2023-03-10)

### Bug Fixes

- **RemoteView**: Support no size at startup
  ([`29c5587`](https://github.com/Kitware/trame-vtk/commit/29c5587f0ca72c78972d6304a48d469231d523e6))


## v2.3.3 (2023-03-10)

### Bug Fixes

- **RemoteView**: Initial still_ratio
  ([`130ff9a`](https://github.com/Kitware/trame-vtk/commit/130ff9a0c146e91ac2230f8cc81fc5eb468d6b73))

fix #25


## v2.3.2 (2023-03-09)

### Bug Fixes

- **serializer**: Add support for LUT components
  ([`3ace3f5`](https://github.com/Kitware/trame-vtk/commit/3ace3f5ffa6e0af6d9db029e0a5ca6fb3f4a7174))


## v2.3.1 (2023-03-09)

### Bug Fixes

- **Serializer**: Properly handle LookupTable size
  ([`95cfd2d`](https://github.com/Kitware/trame-vtk/commit/95cfd2d196bb00e28648f698a63a219e553b54cf))

fix #16


## v2.3.0 (2023-03-09)

### Bug Fixes

- **LocalView**: Add support for vtkAxesActor
  ([`7d21817`](https://github.com/Kitware/trame-vtk/commit/7d21817e7a39f6168081584bf62c81139c6b99d9))

- **vue-vtk-js**: Update to 3.1 to get AxesActor + screenshot
  ([`cfe0b19`](https://github.com/Kitware/trame-vtk/commit/cfe0b19bd22f11ff061031dd2b1ac1980f837d8b))

### Chores

- **debug**: Remote debug output
  ([`aa4f673`](https://github.com/Kitware/trame-vtk/commit/aa4f6739f5e0799773c425606f43e7cdc57d1947))

### Features

- **screenshot**: Allow screenshot extract
  ([`8db1f08`](https://github.com/Kitware/trame-vtk/commit/8db1f0845206fc65ec02f7169aa40ab63bb4d792))


## v2.2.3 (2023-03-03)

### Bug Fixes

- **LocalView**: Allow view update
  ([`034c142`](https://github.com/Kitware/trame-vtk/commit/034c142c17987a28adf30c99b1c72258c8ce6e5b))

### Documentation

- **widget**: Simple plane/clip
  ([`bb95910`](https://github.com/Kitware/trame-vtk/commit/bb9591020966a889885e8a7816c8bd53cfb4a3fc))

- **widget**: Simple plane/clip
  ([`1365d51`](https://github.com/Kitware/trame-vtk/commit/1365d510ebffe0589e3579cbe6b25e8b349626cc))


## v2.2.2 (2023-02-28)

### Bug Fixes

- **widget**: Add a class to wrap vtkAbstractWidgets and make them easier to use
  ([`29e39d4`](https://github.com/Kitware/trame-vtk/commit/29e39d42b7115c6c1df82f7be38c7ecc456aedf5))


## v2.2.1 (2023-02-26)

### Bug Fixes

- **vue3**: Unify template generation
  ([`c13934e`](https://github.com/Kitware/trame-vtk/commit/c13934e20dc5815645ba7f20dd61f831b96d0cd2))

### Documentation

- **example**: Update latest vue3 syntax
  ([`5b64088`](https://github.com/Kitware/trame-vtk/commit/5b64088d05ad5b596758324204092404b8a33f00))


## v2.2.0 (2023-02-25)

### Bug Fixes

- **vue-vtk-js**: Update to latest version
  ([`672e887`](https://github.com/Kitware/trame-vtk/commit/672e88787c5a3c5cbc15b1858291c4131f2f1e50))

### Continuous Integration

- Fix pv import
  ([`4efe9b0`](https://github.com/Kitware/trame-vtk/commit/4efe9b0bcc3531d60f5c500f10e3b2556b964832))

### Documentation

- **example**: Support toggle camera sync
  ([`fb9ab41`](https://github.com/Kitware/trame-vtk/commit/fb9ab41eaf7d9ee25eea3cae98ddab75c00e3611))

### Features

- **LocalRemote**: Allow full camera sync with helper method
  ([`a750af2`](https://github.com/Kitware/trame-vtk/commit/a750af248c5d7025491bca1a8ff6cd0a9bab441b))


## v2.1.0 (2023-02-23)

### Bug Fixes

- **web**: Migrate JS into vue-vtk-js>=3
  ([`9cd279a`](https://github.com/Kitware/trame-vtk/commit/9cd279a3dee3e88aeb0891f370eb65a6a1e3aa1c))

### Features

- **vue23**: Update client code to work with vue2/3
  ([`7a8f546`](https://github.com/Kitware/trame-vtk/commit/7a8f546de013f61f7973118b992fec5889c35690))


## v2.0.18 (2023-02-23)

### Bug Fixes

- **version**: Add __version__
  ([`c9ab451`](https://github.com/Kitware/trame-vtk/commit/c9ab451d9e397f2a9c64b488d957915086a81ddc))

Signed-off-by: Patrick Avery <patrick.avery@kitware.com>

### Continuous Integration

- **semantic-release**: Switch back to master
  ([`e766a8d`](https://github.com/Kitware/trame-vtk/commit/e766a8dc4bbcdb81ebba80af5b509f7f18e7f0b8))

There is an issue in the CI that might be resolved if we switch back to master.

Signed-off-by: Patrick Avery <patrick.avery@kitware.com>


## v2.0.17 (2023-02-01)

### Bug Fixes

- **BigInt**: Add support for LocalView
  ([`aa34620`](https://github.com/Kitware/trame-vtk/commit/aa34620642c64ceb5fd625c83b22fc7f50e823ff))

* fix: support BigInt64Array and BigUint64Array * Update trame_vtk/modules/vtk/addon_serializer.py *
  Add PyVista Int64 validation example * docs(example): Improve int64 validation example *
  fix(BigInt): Update vue-vtk-js

---------

Co-authored-by: Bane Sullivan <bane.sullivan@kitware.com>

### Continuous Integration

- **semantic-release**: Fix version to 7.32.2
  ([`bfa7c41`](https://github.com/Kitware/trame-vtk/commit/bfa7c41d908ebc2c2acbfee4835eccadfc5fb40b))


## v2.0.16 (2023-01-27)

### Bug Fixes

- Imagedata extent and vtkSmartVolumeMapper
  ([`fc096c0`](https://github.com/Kitware/trame-vtk/commit/fc096c0e0190bfef2127aef2f46e3aa9ccdd8893))

* fix: extent with ImageData serializer * Remove dimensions * fix: support vtkSmartVolumeMapper *
  Linting


## v2.0.15 (2023-01-20)

### Bug Fixes

- Cubeaxesserializer colors
  ([`3ea17a4`](https://github.com/Kitware/trame-vtk/commit/3ea17a44f431a0cf8afe4949e7d52c4d631eb4fb))

- **vtk**: Handle CubeAxes grid color + light + disable_auto_switch
  ([`d89c04e`](https://github.com/Kitware/trame-vtk/commit/d89c04e265a28234cd3467866c016247fc5d6e36))


## v2.0.14 (2023-01-10)

### Bug Fixes

- Convert RGB colors to hex
  ([`0be279e`](https://github.com/Kitware/trame-vtk/commit/0be279e6190bcc7c54b9fc725da6df014376656a))


## v2.0.13 (2023-01-10)

### Bug Fixes

- **RemoteLocal**: Fix API call to use delta
  ([`781c282`](https://github.com/Kitware/trame-vtk/commit/781c282b1c812309b1f28ac7c24c69e0506628dd))

- **vue-vtk-js**: Bump version to 2.1.3 to support delta
  ([`8f1d569`](https://github.com/Kitware/trame-vtk/commit/8f1d569e3329ea2a8f7285e06d2083c932bcac10))

fix #9


## v2.0.12 (2022-12-16)

### Bug Fixes

- **LocalView**: Add push_camera
  ([`a9e4513`](https://github.com/Kitware/trame-vtk/commit/a9e4513e43fea443ee02d2de002270d666515913))

- **RemoteView**: Expose still_ratio/quality properties
  ([`7278d5e`](https://github.com/Kitware/trame-vtk/commit/7278d5ed7b8872167a9e9c653792b1b8543ac5ab))


## v2.0.11 (2022-12-09)

### Bug Fixes

- **vue-vtk-js**: Update to 2.1.2
  ([`3cf8913`](https://github.com/Kitware/trame-vtk/commit/3cf8913158e36496e564c4a544f07a2f2cf6c630))


## v2.0.10 (2022-12-04)

### Bug Fixes

- **LocalView**: Add multi-view + delta update handling
  ([`06b6a07`](https://github.com/Kitware/trame-vtk/commit/06b6a0713e91e92ed165f3ec71e4684b988c4d58))

### Documentation

- **example**: Fix flake8 issue
  ([`f80d982`](https://github.com/Kitware/trame-vtk/commit/f80d982011d5b1f9b7e60c1b3b38efba7cab6a80))

- **examples**: Add validation examples
  ([`209914a`](https://github.com/Kitware/trame-vtk/commit/209914ab142fe6bf2f7459a83c4f533d32157212))


## v2.0.9 (2022-11-05)

### Bug Fixes

- **LocalView**: Properly handle add/remove actor
  ([`85ee285`](https://github.com/Kitware/trame-vtk/commit/85ee285f67cf08438d37bae0bfd8d84ffe34db35))


## v2.0.8 (2022-10-20)

### Bug Fixes

- Improve VTK error reporting capabilities
  ([`58b71d3`](https://github.com/Kitware/trame-vtk/commit/58b71d330d0ba8e1afba2c3d3ef918d6090dc193))

- Improve VTK mapper and scalar bar serializers
  ([`fb94e81`](https://github.com/Kitware/trame-vtk/commit/fb94e81ef86c152f207e4fd442747c0d318a8dde))


## v2.0.7 (2022-10-05)

### Bug Fixes

- **VtkLocalView**: Automatically register update on_server_ready
  ([`5b5d296`](https://github.com/Kitware/trame-vtk/commit/5b5d296cc67518801c5ebff9397d55f99461c822))


## v2.0.6 (2022-09-01)

### Bug Fixes

- **VtkPiecewiseEditor**: Expose piecewise editor widget
  ([`1e44b6d`](https://github.com/Kitware/trame-vtk/commit/1e44b6d71f511d19dc95ee42e0d9c981258259b1))

### Chores

- **semantic-release**: Bump version to latest
  ([`ee2d58c`](https://github.com/Kitware/trame-vtk/commit/ee2d58c1c9ba50e704b74a088f90239530a06313))

Signed-off-by: Patrick Avery <patrick.avery@kitware.com>

### Documentation

- **ci**: Add coverage and codecov upload
  ([`b4d7c6e`](https://github.com/Kitware/trame-vtk/commit/b4d7c6ee53917e94ef0a9f5ae27db7cb8af430b6))

Signed-off-by: Patrick Avery <patrick.avery@kitware.com>

- **contributing**: Add CONTRIBUTING.rst
  ([`4bb579d`](https://github.com/Kitware/trame-vtk/commit/4bb579de9779b735f7517d5e47bff15dc6182066))

Signed-off-by: Patrick Avery <patrick.avery@kitware.com>

- **coverage**: Add .coveragerc
  ([`6dd5e1d`](https://github.com/Kitware/trame-vtk/commit/6dd5e1d2ab44ff42ea5510db9aab736e49104b41))

Signed-off-by: Patrick Avery <patrick.avery@kitware.com>

- **coverage**: Remove codecov PR comment
  ([`5cce2fe`](https://github.com/Kitware/trame-vtk/commit/5cce2fe064625de02d6c590b65c925e31e0b36be))

Signed-off-by: Patrick Avery <patrick.avery@kitware.com>

- **readme**: Add CI badge
  ([`214e1bf`](https://github.com/Kitware/trame-vtk/commit/214e1bfb4419a83c6390f1b8bf3cafa75fb3d1c7))

Signed-off-by: Patrick Avery <patrick.avery@kitware.com>


## v2.0.5 (2022-06-01)

### Bug Fixes

- **paraview**: Replace invalid import path
  ([`bd33f2a`](https://github.com/Kitware/trame-vtk/commit/bd33f2a2c71f80792a3039271d70b32f100aeed0))


## v2.0.4 (2022-05-31)

### Bug Fixes

- **widgets**: Expose more props
  ([`2fa0156`](https://github.com/Kitware/trame-vtk/commit/2fa01565461f62f96d3a18b2f649b5484981e5bf))


## v2.0.3 (2022-05-29)

### Bug Fixes

- **js**: Add trame-vtk.js before uploading to pypi
  ([`ec9b1f9`](https://github.com/Kitware/trame-vtk/commit/ec9b1f9e67f43618824459a2a7b6cfbf798dbf64))

Signed-off-by: Patrick Avery <patrick.avery@kitware.com>


## v2.0.2 (2022-05-27)

### Bug Fixes

- **paraview**: Remove unnecessary check for import
  ([`301b684`](https://github.com/Kitware/trame-vtk/commit/301b684378f30d46e93939da67ebd11f2027bf41))

It is okay to check the servermanager import at the time of instantiating the Helper class, and we
  do not need to check for the servermanager when the module is imported.

Signed-off-by: Patrick Avery <patrick.avery@kitware.com>


## v2.0.1 (2022-05-27)

### Bug Fixes

- Add initial CI, including semantic release
  ([`2f72dda`](https://github.com/Kitware/trame-vtk/commit/2f72dda6bf851b8afea1f1cf34d616554b5b5dfc))

Signed-off-by: Patrick Avery <patrick.avery@kitware.com>
