# Changelog

<!--next-version-placeholder-->

## v2.0.18 (2023-02-23)
### Fix
* **version:** Add __version__ ([`c9ab451`](https://github.com/Kitware/trame-vtk/commit/c9ab451d9e397f2a9c64b488d957915086a81ddc))

## v2.0.17 (2023-02-01)
### Fix
* **BigInt:** Add support for LocalView ([`aa34620`](https://github.com/Kitware/trame-vtk/commit/aa34620642c64ceb5fd625c83b22fc7f50e823ff))

## v2.0.16 (2023-01-27)
### Fix
* ImageData extent and vtkSmartVolumeMapper ([`fc096c0`](https://github.com/Kitware/trame-vtk/commit/fc096c0e0190bfef2127aef2f46e3aa9ccdd8893))

## v2.0.15 (2023-01-20)
### Fix
* **vtk:** Handle CubeAxes grid color + light + disable_auto_switch ([`d89c04e`](https://github.com/Kitware/trame-vtk/commit/d89c04e265a28234cd3467866c016247fc5d6e36))
* CubeAxesSerializer colors ([`3ea17a4`](https://github.com/Kitware/trame-vtk/commit/3ea17a44f431a0cf8afe4949e7d52c4d631eb4fb))

## v2.0.14 (2023-01-10)
### Fix
* Convert RGB colors to hex ([`0be279e`](https://github.com/Kitware/trame-vtk/commit/0be279e6190bcc7c54b9fc725da6df014376656a))

## v2.0.13 (2023-01-10)
### Fix
* **vue-vtk-js:** Bump version to 2.1.3 to support delta ([`8f1d569`](https://github.com/Kitware/trame-vtk/commit/8f1d569e3329ea2a8f7285e06d2083c932bcac10))
* **RemoteLocal:** Fix API call to use delta ([`781c282`](https://github.com/Kitware/trame-vtk/commit/781c282b1c812309b1f28ac7c24c69e0506628dd))

## v2.0.12 (2022-12-16)
### Fix
* **RemoteView:** Expose still_ratio/quality properties ([`7278d5e`](https://github.com/Kitware/trame-vtk/commit/7278d5ed7b8872167a9e9c653792b1b8543ac5ab))
* **LocalView:** Add push_camera ([`a9e4513`](https://github.com/Kitware/trame-vtk/commit/a9e4513e43fea443ee02d2de002270d666515913))

## v2.0.11 (2022-12-09)
### Fix
* **vue-vtk-js:** Update to 2.1.2 ([`3cf8913`](https://github.com/Kitware/trame-vtk/commit/3cf8913158e36496e564c4a544f07a2f2cf6c630))

## v2.0.10 (2022-12-04)
### Fix
* **LocalView:** Add multi-view + delta update handling ([`06b6a07`](https://github.com/Kitware/trame-vtk/commit/06b6a0713e91e92ed165f3ec71e4684b988c4d58))

### Documentation
* **example:** Fix flake8 issue ([`f80d982`](https://github.com/Kitware/trame-vtk/commit/f80d982011d5b1f9b7e60c1b3b38efba7cab6a80))
* **examples:** Add validation examples ([`209914a`](https://github.com/Kitware/trame-vtk/commit/209914ab142fe6bf2f7459a83c4f533d32157212))

## v2.0.9 (2022-11-05)
### Fix
* **LocalView:** Properly handle add/remove actor ([`85ee285`](https://github.com/Kitware/trame-vtk/commit/85ee285f67cf08438d37bae0bfd8d84ffe34db35))

## v2.0.8 (2022-10-20)
### Fix
* Improve VTK mapper and scalar bar serializers ([`fb94e81`](https://github.com/Kitware/trame-vtk/commit/fb94e81ef86c152f207e4fd442747c0d318a8dde))
* Improve VTK error reporting capabilities ([`58b71d3`](https://github.com/Kitware/trame-vtk/commit/58b71d330d0ba8e1afba2c3d3ef918d6090dc193))

## v2.0.7 (2022-10-05)
### Fix
* **VtkLocalView:** Automatically register update on_server_ready ([`5b5d296`](https://github.com/Kitware/trame-vtk/commit/5b5d296cc67518801c5ebff9397d55f99461c822))

## v2.0.6 (2022-09-01)
### Fix
* **VtkPiecewiseEditor:** Expose piecewise editor widget ([`1e44b6d`](https://github.com/Kitware/trame-vtk/commit/1e44b6d71f511d19dc95ee42e0d9c981258259b1))

### Documentation
* **coverage:** Remove codecov PR comment ([`5cce2fe`](https://github.com/Kitware/trame-vtk/commit/5cce2fe064625de02d6c590b65c925e31e0b36be))
* **coverage:** Add .coveragerc ([`6dd5e1d`](https://github.com/Kitware/trame-vtk/commit/6dd5e1d2ab44ff42ea5510db9aab736e49104b41))
* **ci:** Add coverage and codecov upload ([`b4d7c6e`](https://github.com/Kitware/trame-vtk/commit/b4d7c6ee53917e94ef0a9f5ae27db7cb8af430b6))
* **readme:** Add CI badge ([`214e1bf`](https://github.com/Kitware/trame-vtk/commit/214e1bfb4419a83c6390f1b8bf3cafa75fb3d1c7))
* **contributing:** Add CONTRIBUTING.rst ([`4bb579d`](https://github.com/Kitware/trame-vtk/commit/4bb579de9779b735f7517d5e47bff15dc6182066))

## v2.0.5 (2022-06-01)
### Fix
* **paraview:** Replace invalid import path ([`bd33f2a`](https://github.com/Kitware/trame-vtk/commit/bd33f2a2c71f80792a3039271d70b32f100aeed0))

## v2.0.4 (2022-05-31)
### Fix
* **widgets:** Expose more props ([`2fa0156`](https://github.com/Kitware/trame-vtk/commit/2fa01565461f62f96d3a18b2f649b5484981e5bf))

## v2.0.3 (2022-05-29)
### Fix
* **js:** Add trame-vtk.js before uploading to pypi ([`ec9b1f9`](https://github.com/Kitware/trame-vtk/commit/ec9b1f9e67f43618824459a2a7b6cfbf798dbf64))

## v2.0.2 (2022-05-27)
### Fix
* **paraview:** Remove unnecessary check for import ([`301b684`](https://github.com/Kitware/trame-vtk/commit/301b684378f30d46e93939da67ebd11f2027bf41))

## v2.0.1 (2022-05-27)
### Fix
* Add initial CI, including semantic release ([`2f72dda`](https://github.com/Kitware/trame-vtk/commit/2f72dda6bf851b8afea1f1cf34d616554b5b5dfc))
