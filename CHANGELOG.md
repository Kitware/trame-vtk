# CHANGELOG



## v2.5.6 (2023-07-19)

### Ci

* ci(baseline): Add ref baseline for volume ([`4ceb45c`](https://github.com/Kitware/trame-vtk/commit/4ceb45c968a51e0cc5482160bc3ded3de23db352))

* ci(baseline): Add ref baselines ([`8b305e6`](https://github.com/Kitware/trame-vtk/commit/8b305e64550ed62a68db6589b0f6b9b9de386d07))

* ci: changelog spelling ([`6d3b6f5`](https://github.com/Kitware/trame-vtk/commit/6d3b6f5c7acce73d81307f58091d64f9750311c0))

* ci(testing): rendering testing

fix #45 ([`70aeafa`](https://github.com/Kitware/trame-vtk/commit/70aeafa443617c2ac7e6f017769e6d7751d8a7b5))

### Fix

* fix(VolumeRendering): Add alias to support different mappers

fix #46
fix #44 ([`cf540bc`](https://github.com/Kitware/trame-vtk/commit/cf540bc7472072ff9d8d379ca4905ee8b0fb82f2))


## v2.5.5 (2023-07-19)

### Chore

* chore(volume): Add volume rendering example ([`672b1ad`](https://github.com/Kitware/trame-vtk/commit/672b1adb979bb865d3379bd6a947c8546d587022))

### Ci

* ci: upate baselines ([`68e1a2d`](https://github.com/Kitware/trame-vtk/commit/68e1a2db3a86742fa353d1032807459da57557e9))

* ci: upate baselines ([`082de9c`](https://github.com/Kitware/trame-vtk/commit/082de9c79f8a7b653bb5c71482e2bea97b050a49))

### Fix

* fix(ParaView): push_image for different viewtypes

Not using a RenderView as view for the vtkLocalRemoteView will crash, because &#34;EnableRenderOnInteraction&#34; might not be defined. &#34;GetPropertyValue&#34; will return None for a non-existing Property ([`74ed533`](https://github.com/Kitware/trame-vtk/commit/74ed533a2a29930b2f33d0dd2fb77c30987a51e2))


## v2.5.4 (2023-06-29)

### Ci

* ci: use better stage name ([`0bf3f73`](https://github.com/Kitware/trame-vtk/commit/0bf3f73b2257f2e49552d69ed2c5ad8f909e6487))

* ci: add missing requirements ([`17407e3`](https://github.com/Kitware/trame-vtk/commit/17407e3f1edbfdca8dbdba37d15464e948567a58))

* ci: add gc testing ([`ef361f7`](https://github.com/Kitware/trame-vtk/commit/ef361f794728cf0b15c70f42c1e562d7cdcbcb6a))

### Fix

* fix(GC): Allow to release view resources ([`bfe9c80`](https://github.com/Kitware/trame-vtk/commit/bfe9c8048b04fd41d72e150c009e33137a9e3e64))


## v2.5.3 (2023-06-28)

### Fix

* fix(html): Improve HTML exporting (#42) ([`3a0184e`](https://github.com/Kitware/trame-vtk/commit/3a0184e86842f275d920827c3e1a5bb62f627655))


## v2.5.2 (2023-06-26)

### Ci

* ci(testing): Update baselines ([`d5b34a4`](https://github.com/Kitware/trame-vtk/commit/d5b34a4c06d977048e10d70c15cc4b482ba67efe))

* ci(testing): Update baselines ([`0d6e494`](https://github.com/Kitware/trame-vtk/commit/0d6e4945f80ee56b7ecc8181d4341331989b7d0e))

### Fix

* fix(vue-vtk-js): Update to pick lookuptable fix ([`1ecd65c`](https://github.com/Kitware/trame-vtk/commit/1ecd65cf9539b1dfec912e3d85560e0df794409b))

* fix(html): Add tool for HTML export ([`3705560`](https://github.com/Kitware/trame-vtk/commit/3705560873ee0c9c4b846fe93568391a105d192d))


## v2.5.1 (2023-06-23)

### Ci

* ci: split steps ([`b1fdde6`](https://github.com/Kitware/trame-vtk/commit/b1fdde61d96681a9f052d4c75628367f1fe4069c))

* ci: add browser testing ([`a804d55`](https://github.com/Kitware/trame-vtk/commit/a804d5516b7a57ea25807cf55b4b6bcaabdcdda4))

### Fix

* fix(LUT): Do not discretize vtkColorTransferFunction with few control points ([`ebfaee4`](https://github.com/Kitware/trame-vtk/commit/ebfaee4f3abadb0e418beaa56d1de4e410425947))


## v2.5.0 (2023-06-16)

### Ci

* ci: Add test baseline ([`5ad9763`](https://github.com/Kitware/trame-vtk/commit/5ad976321869b205543c12d52b4675dde5776be4))

* ci(black): run black ([`dfdc6fa`](https://github.com/Kitware/trame-vtk/commit/dfdc6fa6768a549362dbd3114beb7d08b94b18c7))

### Documentation

* docs(validation): Add lut preset example ([`3250926`](https://github.com/Kitware/trame-vtk/commit/3250926e6c050022cb28c6b60b95e18e2217c66f))

* docs(example): force reset camera in pyvista ([`d083796`](https://github.com/Kitware/trame-vtk/commit/d08379621902bc541e8f12a5e0716aa70f55249d))

### Feature

* feat(local): Enable prop caching ([`be29552`](https://github.com/Kitware/trame-vtk/commit/be29552102b0394ae3e45bcc96a0c6b4f2af73dc))

* feat(local): Add caching with delta compute for local state ([`0d64fbb`](https://github.com/Kitware/trame-vtk/commit/0d64fbb836bec479c17045be57d4143734330aa3))

### Fix

* fix(vue-vtk-js): Update vtk.js ([`96e569a`](https://github.com/Kitware/trame-vtk/commit/96e569ac37140baa643cfa14bf270c3fa388d2e2))

* fix(LookupTable): Add support for color Table ([`46e3d6d`](https://github.com/Kitware/trame-vtk/commit/46e3d6d7ee05e4adcf7f664ae1e2f4ffe3188b7d))

* fix(local): Keep vtkLookupTable as-is for vtk.js ([`a3b1904`](https://github.com/Kitware/trame-vtk/commit/a3b19046bf26e7e11a8d7d10063301b625cba2a0))


## v2.4.4 (2023-04-16)

### Documentation

* docs(pv): Add paraview validation example ([`9146694`](https://github.com/Kitware/trame-vtk/commit/914669478cb2ba088131d8da81ddc287003afb23))

### Fix

* fix(export): handle fields for offline rendering ([`8b9920f`](https://github.com/Kitware/trame-vtk/commit/8b9920fdc7328d8fa20bd3d6c3d2566f1175d883))

* fix(ParaView): Add missing widgets args in scene ([`47c4f0e`](https://github.com/Kitware/trame-vtk/commit/47c4f0efc3ad2feed4a12901a33e1442aab15b29))


## v2.4.3 (2023-04-07)

### Fix

* fix(export): Add export for VtkLocalView ([`b58ccf4`](https://github.com/Kitware/trame-vtk/commit/b58ccf4109b25f567cac0f8f1185ab71e00c14dc))


## v2.4.2 (2023-03-31)

### Documentation

* docs(examples): simplify code ([`b9afcea`](https://github.com/Kitware/trame-vtk/commit/b9afceadd32a565aef380ec148a05d014e115687))

* docs(examples): Add button toggles for widgets ([`ed307b3`](https://github.com/Kitware/trame-vtk/commit/ed307b32b888e9698e87f5f6af14b5f3cb2e4d8f))

* docs(examples): Update the widget ones ([`cdda471`](https://github.com/Kitware/trame-vtk/commit/cdda471df5c2364e7359c2d6533ffcd4e4b38cf0))

* docs(examples): add pyvista axes widget examples ([`b1598f6`](https://github.com/Kitware/trame-vtk/commit/b1598f61c6a53d77acd5688026560069153e6886))

### Fix

* fix(vue-vtk-js): bump version of vue-vtk-js

Signed-off-by: Patrick Avery &lt;patrick.avery@kitware.com&gt; ([`11c14b9`](https://github.com/Kitware/trame-vtk/commit/11c14b9b19a6fe1d8019c63c2d94806caf438954))

* fix(widgets): Use proper order initialization ([`f3c0505`](https://github.com/Kitware/trame-vtk/commit/f3c05053a81786fc1627cd55f5a360b580c52a10))

* fix(VtkRemoteLocalView): add support for widgets ([`79d106a`](https://github.com/Kitware/trame-vtk/commit/79d106ac2ffb432517bef8f57d80551ff699466d))

* fix(behavior): Implement handler for vtkOrientationMarkerWidget ([`01e035f`](https://github.com/Kitware/trame-vtk/commit/01e035ff6f8f3fd52717b627f6db57961f4debc1))

* fix(LocalView): add infrastructure to support behaviors ([`26e1945`](https://github.com/Kitware/trame-vtk/commit/26e194535c2e5ca910ebc053b16bd7abacd91cbe))

### Unknown

* Merge pull request #34 from Kitware/add-behavior-to-localview

fix(LocalView): add infrastructure to support behaviors ([`74b6b1c`](https://github.com/Kitware/trame-vtk/commit/74b6b1c47bc9d05c8d53423381edbe161f573c52))


## v2.4.1 (2023-03-27)

### Fix

* fix(paraview): Fix protocol ([`b72425c`](https://github.com/Kitware/trame-vtk/commit/b72425cdde30344b15cebf8dd1b11aa62701176f))


## v2.4.0 (2023-03-24)

### Chore

* chore(checks): remove checks for wslink

It is required and we don&#39;t need to check for its presence.

Signed-off-by: Patrick Avery &lt;patrick.avery@kitware.com&gt; ([`5fea67d`](https://github.com/Kitware/trame-vtk/commit/5fea67d77d09f9f6468f63814c617d9d3e1f6786))

* chore(future): remove unneeded future imports

Signed-off-by: Patrick Avery &lt;patrick.avery@kitware.com&gt; ([`dd57968`](https://github.com/Kitware/trame-vtk/commit/dd579681599e658cc891f93f7494f97556d03de6))

### Feature

* feat(protocols): copy protocols from VTK exactly

This copies the protocols and render_window_serializer from VTK exactly as they are. Further
commits will modify the code.

Signed-off-by: Patrick Avery &lt;patrick.avery@kitware.com&gt; ([`9fe3c26`](https://github.com/Kitware/trame-vtk/commit/9fe3c261bc78a8814e1f4bab37ac6df3977144d8))

### Fix

* fix(messages): only print no serializer warning once per instance type

Signed-off-by: Patrick Avery &lt;patrick.avery@kitware.com&gt; ([`65db322`](https://github.com/Kitware/trame-vtk/commit/65db3229b9b0d15183a3fa882a825b4a9ea745ea))

* fix(logger): add environment variable for setting serializer log level

Now, only critical messages from serializers are printed by default, unless the
`TRAME_SERIALIZE_DEBUG` environment variable is set, in which case all logger output will be
printed from the serializers.

Signed-off-by: Patrick Avery &lt;patrick.avery@kitware.com&gt; ([`3c1614c`](https://github.com/Kitware/trame-vtk/commit/3c1614c82f47528e71de69916baa22961177c3d9))

* fix(paraview): update mouse wheel to match VTK version

Signed-off-by: Patrick Avery &lt;patrick.avery@kitware.com&gt; ([`6f93186`](https://github.com/Kitware/trame-vtk/commit/6f931867e3b63aa59e03799495ade03c59b31abf))

* fix(helper): update name to `_trame_server`

This is the correct name

Signed-off-by: Patrick Avery &lt;patrick.avery@kitware.com&gt; ([`2b2b607`](https://github.com/Kitware/trame-vtk/commit/2b2b607da8abc3639b791c4411ffb22d9d3a147c))

* fix(vue-vtk-js): upgrade to prevent client error on unmount

Signed-off-by: Patrick Avery &lt;patrick.avery@kitware.com&gt; ([`3a2acee`](https://github.com/Kitware/trame-vtk/commit/3a2aceececd6f70e2bc4e78c309b051723eb9d45))

* fix(mouse_handler): only trigger animation registration on first &#34;down&#34;

This was copied over from the ParaView version of the mouse handler.

Signed-off-by: Patrick Avery &lt;patrick.avery@kitware.com&gt; ([`88bac50`](https://github.com/Kitware/trame-vtk/commit/88bac500cbd3d6f3775a7cab9170c775a5683ff6))

* fix(mouse_handler): apply a couple of fixes to mouse wheel event

First of all, this updates the interactor with the mouse position on a wheel event so that if there
are multiple renderers, the interactor can figure out which one needs to be updated.

Second, this forwards the event to the interactor, rather than applying a manual zoom to the
camera ourselves. This makes the behavior more consistent.

Third, this skips the zoom for the start event, since there appears to always be a wheel event
right after it.

Fixes: pyvista/pyvista#4020

Signed-off-by: Patrick Avery &lt;patrick.avery@kitware.com&gt; ([`45505ef`](https://github.com/Kitware/trame-vtk/commit/45505ef25bb76a4d04bddd9cecdc375999de9e1b))

* fix(vue-vtk-js): update vue-vtk-js to the newest version

This includes mouse position information for moving the mouse wheel,
which we need.

Signed-off-by: Patrick Avery &lt;patrick.avery@kitware.com&gt; ([`eb7310d`](https://github.com/Kitware/trame-vtk/commit/eb7310dd9e763b069de438ad33db3173965c2e81))

### Refactor

* refactor(registry): remove unused context variable

Signed-off-by: Patrick Avery &lt;patrick.avery@kitware.com&gt; ([`5fd2640`](https://github.com/Kitware/trame-vtk/commit/5fd26407a1077874d7427c49407c7cf8d55bbb8e))

* refactor(case): convert most variables from camelCase to snake_case

I went through the code and automatically converted most of the variables from camelCase to
snake_case using regex in vim. I skipped a couple of cases in particular:

1. Anything that started with `vtk` (this might be a VTK object)
2. Anything in quotes (since they might be strings sent to VTK.js)

There were, however, some things still that were modified that should not have been. I tried to
manually fix these, but I may have not caught everything, so we should do testing to verify.

Signed-off-by: Patrick Avery &lt;patrick.avery@kitware.com&gt; ([`ba9beaf`](https://github.com/Kitware/trame-vtk/commit/ba9beaf5060ab2b992a85d7ae701f3f4853deba2))

* refactor(updateZoomFromWheel): remove duplicated code

Signed-off-by: Patrick Avery &lt;patrick.avery@kitware.com&gt; ([`c9c07da`](https://github.com/Kitware/trame-vtk/commit/c9c07da41b71ecfbd6afa65db7ceeaf0609c5572))

* refactor(pwf): move pwf serializer into lookup_tables

Signed-off-by: Patrick Avery &lt;patrick.avery@kitware.com&gt; ([`1ef8fd9`](https://github.com/Kitware/trame-vtk/commit/1ef8fd97682e262214e80dbde7889617c5a9c40c))

* refactor(serializers): move one directory up

It should be a sibling of the protocols, not a child.

Signed-off-by: Patrick Avery &lt;patrick.avery@kitware.com&gt; ([`bd6c3da`](https://github.com/Kitware/trame-vtk/commit/bd6c3da1caf27837a7691ce95437155970473692))

* refactor(paraview): fix import path for vtk_mesh

Signed-off-by: Patrick Avery &lt;patrick.avery@kitware.com&gt; ([`b3578a7`](https://github.com/Kitware/trame-vtk/commit/b3578a7d3b8aabb6ef0fa3b76c5280b3ba9e0c62))

* refactor(paraview): copy paraview protocols into repo

This also splits them up into separate files.

Signed-off-by: Patrick Avery &lt;patrick.avery@kitware.com&gt; ([`43fdc97`](https://github.com/Kitware/trame-vtk/commit/43fdc97989a16f5bf72b9d73ce7a591523acecf9))

* refactor(serialize): break up serializers into separate files

Signed-off-by: Patrick Avery &lt;patrick.avery@kitware.com&gt; ([`57d5f0d`](https://github.com/Kitware/trame-vtk/commit/57d5f0debab099e5918fed00e1c66c9556bd22b6))

* refactor(serializers): move into subdirectory

The file will be broken apart soon as well.

Signed-off-by: Patrick Avery &lt;patrick.avery@kitware.com&gt; ([`114a83b`](https://github.com/Kitware/trame-vtk/commit/114a83b5ac4265a9d989b85ef0e389367fc10b76))

* refactor(protocols): remove unused protocols

Signed-off-by: Patrick Avery &lt;patrick.avery@kitware.com&gt; ([`d24e998`](https://github.com/Kitware/trame-vtk/commit/d24e9984d46b2bea194ea3e8a15a7208bfeba00c))

* refactor(render_window_serializer): rename to serializers

This name fits better since it contains all kinds of serializers.

Signed-off-by: Patrick Avery &lt;patrick.avery@kitware.com&gt; ([`1bec149`](https://github.com/Kitware/trame-vtk/commit/1bec1497279b1c95337bf9245ab7bfcccd730810))

* refactor(initializeSerializers()): reduce repetition

Signed-off-by: Patrick Avery &lt;patrick.avery@kitware.com&gt; ([`7e8b213`](https://github.com/Kitware/trame-vtk/commit/7e8b21332a3c4b3edd901047fb0568ec169012ed))

* refactor(serializers): apply patches from addon_serializer

This takes the patches being applied in addon_serializer.py and puts them directly in the
render window serializer. We should verify that there are no issues. But I did notice some
discrepancies:

1. I saw no difference in `extractRequiredFields()`
2. The addon serializer did not call `registerInstanceSerializer()` on `vtkStructuredPoints` with
the modified `imagedataSerializer` (only difference is that extent is used instead of dimensions).
3. The addon serializer did not call `registerInstanceSerializer()` on `vtkColorTransferFunction` with
the modified `colorTransferFunctionSerializer`.
4. `genericMapperSerializer()` only had debug message modifications

Signed-off-by: Patrick Avery &lt;patrick.avery@kitware.com&gt; ([`a93a540`](https://github.com/Kitware/trame-vtk/commit/a93a5400f542c529024e18941f9323c7623cea12))

* refactor(web): remove last use of vtkmodules.web

The functions being used were copied over.

Signed-off-by: Patrick Avery &lt;patrick.avery@kitware.com&gt; ([`fcef60a`](https://github.com/Kitware/trame-vtk/commit/fcef60a42f19dac24bdede46ccda98758b75b8eb))

* refactor(utils): copy utils from vtk web

This is one less dependency we need from vtkmodules.web

Signed-off-by: Patrick Avery &lt;patrick.avery@kitware.com&gt; ([`d338893`](https://github.com/Kitware/trame-vtk/commit/d338893528675ba17d24ed9c386ec27cfac67656))

* refactor(protocols): use local versions of protocols

This appears to be working at least on a basic level.

Signed-off-by: Patrick Avery &lt;patrick.avery@kitware.com&gt; ([`315f06f`](https://github.com/Kitware/trame-vtk/commit/315f06fc99acf293c6dcbc6fc2457f1880cd07f1))

* refactor(protocols): break up protocols into separate files

Signed-off-by: Patrick Avery &lt;patrick.avery@kitware.com&gt; ([`7336447`](https://github.com/Kitware/trame-vtk/commit/73364475eb881b1752779ee558f1d87ad4a2f327))

### Style

* style(formatting): fix flake8 and black issues

Signed-off-by: Patrick Avery &lt;patrick.avery@kitware.com&gt; ([`e69c80c`](https://github.com/Kitware/trame-vtk/commit/e69c80c64cce9b3cbd827a27efb743d5edf9e76f))

### Unknown

* Merge pull request #31 from Kitware/vtk-protocols

Transfer VTK protocols and serializers to trame-vtk ([`8b779f7`](https://github.com/Kitware/trame-vtk/commit/8b779f77268aab390eb2fcfa22a5c3bfa9ec953c))


## v2.3.5 (2023-03-21)

### Fix

* fix: axes serializer ([`cc2136d`](https://github.com/Kitware/trame-vtk/commit/cc2136df0d4ff850f25f791ffc76f3ae2ba10a92))


## v2.3.4 (2023-03-10)

### Fix

* fix(RemoteView): Support no size at startup ([`29c5587`](https://github.com/Kitware/trame-vtk/commit/29c5587f0ca72c78972d6304a48d469231d523e6))


## v2.3.3 (2023-03-10)

### Fix

* fix(RemoteView): Initial still_ratio

fix #25 ([`130ff9a`](https://github.com/Kitware/trame-vtk/commit/130ff9a0c146e91ac2230f8cc81fc5eb468d6b73))


## v2.3.2 (2023-03-09)

### Fix

* fix(serializer): Add support for LUT components ([`3ace3f5`](https://github.com/Kitware/trame-vtk/commit/3ace3f5ffa6e0af6d9db029e0a5ca6fb3f4a7174))


## v2.3.1 (2023-03-09)

### Fix

* fix(Serializer): Properly handle LookupTable size

fix #16 ([`95cfd2d`](https://github.com/Kitware/trame-vtk/commit/95cfd2d196bb00e28648f698a63a219e553b54cf))


## v2.3.0 (2023-03-09)

### Chore

* chore(debug): Remote debug output ([`aa4f673`](https://github.com/Kitware/trame-vtk/commit/aa4f6739f5e0799773c425606f43e7cdc57d1947))

### Feature

* feat(screenshot): Allow screenshot extract ([`8db1f08`](https://github.com/Kitware/trame-vtk/commit/8db1f0845206fc65ec02f7169aa40ab63bb4d792))

### Fix

* fix(vue-vtk-js): Update to 3.1 to get AxesActor + screenshot ([`cfe0b19`](https://github.com/Kitware/trame-vtk/commit/cfe0b19bd22f11ff061031dd2b1ac1980f837d8b))

* fix(LocalView): Add support for vtkAxesActor ([`7d21817`](https://github.com/Kitware/trame-vtk/commit/7d21817e7a39f6168081584bf62c81139c6b99d9))


## v2.2.3 (2023-03-03)

### Documentation

* docs(widget): Simple plane/clip ([`bb95910`](https://github.com/Kitware/trame-vtk/commit/bb9591020966a889885e8a7816c8bd53cfb4a3fc))

* docs(widget): Simple plane/clip ([`1365d51`](https://github.com/Kitware/trame-vtk/commit/1365d510ebffe0589e3579cbe6b25e8b349626cc))

### Fix

* fix(LocalView): Allow view update ([`034c142`](https://github.com/Kitware/trame-vtk/commit/034c142c17987a28adf30c99b1c72258c8ce6e5b))


## v2.2.2 (2023-02-28)

### Fix

* fix(widget): Add a class to wrap vtkAbstractWidgets and make them easier to use ([`29e39d4`](https://github.com/Kitware/trame-vtk/commit/29e39d42b7115c6c1df82f7be38c7ecc456aedf5))


## v2.2.1 (2023-02-26)

### Documentation

* docs(example): Update latest vue3 syntax ([`5b64088`](https://github.com/Kitware/trame-vtk/commit/5b64088d05ad5b596758324204092404b8a33f00))

### Fix

* fix(vue3): unify template generation ([`c13934e`](https://github.com/Kitware/trame-vtk/commit/c13934e20dc5815645ba7f20dd61f831b96d0cd2))


## v2.2.0 (2023-02-25)

### Ci

* ci: fix pv import ([`4efe9b0`](https://github.com/Kitware/trame-vtk/commit/4efe9b0bcc3531d60f5c500f10e3b2556b964832))

### Documentation

* docs(example): Support toggle camera sync ([`fb9ab41`](https://github.com/Kitware/trame-vtk/commit/fb9ab41eaf7d9ee25eea3cae98ddab75c00e3611))

### Feature

* feat(LocalRemote): Allow full camera sync with helper method ([`a750af2`](https://github.com/Kitware/trame-vtk/commit/a750af248c5d7025491bca1a8ff6cd0a9bab441b))

### Fix

* fix(vue-vtk-js): Update to latest version ([`672e887`](https://github.com/Kitware/trame-vtk/commit/672e88787c5a3c5cbc15b1858291c4131f2f1e50))


## v2.1.0 (2023-02-23)

### Feature

* feat(vue23): Update client code to work with vue2/3 ([`7a8f546`](https://github.com/Kitware/trame-vtk/commit/7a8f546de013f61f7973118b992fec5889c35690))

### Fix

* fix(web): Migrate JS into vue-vtk-js&gt;=3 ([`9cd279a`](https://github.com/Kitware/trame-vtk/commit/9cd279a3dee3e88aeb0891f370eb65a6a1e3aa1c))


## v2.0.18 (2023-02-23)

### Ci

* ci(semantic-release): switch back to master

There is an issue in the CI that might be resolved if we switch back to master.

Signed-off-by: Patrick Avery &lt;patrick.avery@kitware.com&gt; ([`e766a8d`](https://github.com/Kitware/trame-vtk/commit/e766a8dc4bbcdb81ebba80af5b509f7f18e7f0b8))

### Fix

* fix(version): add __version__

Signed-off-by: Patrick Avery &lt;patrick.avery@kitware.com&gt; ([`c9ab451`](https://github.com/Kitware/trame-vtk/commit/c9ab451d9e397f2a9c64b488d957915086a81ddc))


## v2.0.17 (2023-02-01)

### Ci

* ci(semantic-release): Fix version to 7.32.2 ([`bfa7c41`](https://github.com/Kitware/trame-vtk/commit/bfa7c41d908ebc2c2acbfee4835eccadfc5fb40b))

### Fix

* fix(BigInt): Add support for LocalView

* fix: support BigInt64Array and BigUint64Array
* Update trame_vtk/modules/vtk/addon_serializer.py
* Add PyVista Int64 validation example
* docs(example): Improve int64 validation example
* fix(BigInt): Update vue-vtk-js

---------

Co-authored-by: Bane Sullivan &lt;bane.sullivan@kitware.com&gt; ([`aa34620`](https://github.com/Kitware/trame-vtk/commit/aa34620642c64ceb5fd625c83b22fc7f50e823ff))


## v2.0.16 (2023-01-27)

### Fix

* fix: ImageData extent and vtkSmartVolumeMapper

* fix: extent with ImageData serializer
* Remove dimensions
* fix: support vtkSmartVolumeMapper
* Linting ([`fc096c0`](https://github.com/Kitware/trame-vtk/commit/fc096c0e0190bfef2127aef2f46e3aa9ccdd8893))


## v2.0.15 (2023-01-20)

### Fix

* fix(vtk): Handle CubeAxes grid color + light + disable_auto_switch ([`d89c04e`](https://github.com/Kitware/trame-vtk/commit/d89c04e265a28234cd3467866c016247fc5d6e36))

* fix: cubeAxesSerializer colors ([`3ea17a4`](https://github.com/Kitware/trame-vtk/commit/3ea17a44f431a0cf8afe4949e7d52c4d631eb4fb))

### Unknown

* Merge pull request #13 from Kitware/grid-axis

Grid axis ([`99cfe9c`](https://github.com/Kitware/trame-vtk/commit/99cfe9cb4259884c9ce836cba7adc9d0a354c429))


## v2.0.14 (2023-01-10)

### Fix

* fix: convert RGB colors to hex ([`0be279e`](https://github.com/Kitware/trame-vtk/commit/0be279e6190bcc7c54b9fc725da6df014376656a))

### Unknown

* Merge pull request #10 from banesullivan/patch-2

fix: convert RGB colors to hex ([`bbb700b`](https://github.com/Kitware/trame-vtk/commit/bbb700bc58691307046ba4950019b9bb2d1438b3))


## v2.0.13 (2023-01-10)

### Fix

* fix(vue-vtk-js): Bump version to 2.1.3 to support delta

fix #9 ([`8f1d569`](https://github.com/Kitware/trame-vtk/commit/8f1d569e3329ea2a8f7285e06d2083c932bcac10))

* fix(RemoteLocal): Fix API call to use delta ([`781c282`](https://github.com/Kitware/trame-vtk/commit/781c282b1c812309b1f28ac7c24c69e0506628dd))


## v2.0.12 (2022-12-16)

### Fix

* fix(RemoteView): Expose still_ratio/quality properties ([`7278d5e`](https://github.com/Kitware/trame-vtk/commit/7278d5ed7b8872167a9e9c653792b1b8543ac5ab))

* fix(LocalView): Add push_camera ([`a9e4513`](https://github.com/Kitware/trame-vtk/commit/a9e4513e43fea443ee02d2de002270d666515913))


## v2.0.11 (2022-12-09)

### Fix

* fix(vue-vtk-js): Update to 2.1.2 ([`3cf8913`](https://github.com/Kitware/trame-vtk/commit/3cf8913158e36496e564c4a544f07a2f2cf6c630))


## v2.0.10 (2022-12-04)

### Documentation

* docs(example): fix flake8 issue ([`f80d982`](https://github.com/Kitware/trame-vtk/commit/f80d982011d5b1f9b7e60c1b3b38efba7cab6a80))

* docs(examples): add validation examples ([`209914a`](https://github.com/Kitware/trame-vtk/commit/209914ab142fe6bf2f7459a83c4f533d32157212))

### Fix

* fix(LocalView): Add multi-view + delta update handling ([`06b6a07`](https://github.com/Kitware/trame-vtk/commit/06b6a0713e91e92ed165f3ec71e4684b988c4d58))


## v2.0.9 (2022-11-05)

### Fix

* fix(LocalView): Properly handle add/remove actor ([`85ee285`](https://github.com/Kitware/trame-vtk/commit/85ee285f67cf08438d37bae0bfd8d84ffe34db35))


## v2.0.8 (2022-10-20)

### Fix

* fix: improve VTK mapper and scalar bar serializers ([`fb94e81`](https://github.com/Kitware/trame-vtk/commit/fb94e81ef86c152f207e4fd442747c0d318a8dde))

* fix: Improve VTK error reporting capabilities ([`58b71d3`](https://github.com/Kitware/trame-vtk/commit/58b71d330d0ba8e1afba2c3d3ef918d6090dc193))

### Unknown

* Merge pull request #4 from banesullivan/patch/vtk-web-import

fix: Improve VTK error reporting capabilities ([`28a992a`](https://github.com/Kitware/trame-vtk/commit/28a992aad9ed13372a65456ce5202db83b47ef38))

* Merge pull request #5 from banesullivan/fix-serializers

fix: improve VTK mapper and scalar bar serializers ([`b25a9b1`](https://github.com/Kitware/trame-vtk/commit/b25a9b1724e4c71de5152d149fd1853d335c2478))


## v2.0.7 (2022-10-05)

### Fix

* fix(VtkLocalView): Automatically register update on_server_ready ([`5b5d296`](https://github.com/Kitware/trame-vtk/commit/5b5d296cc67518801c5ebff9397d55f99461c822))

### Unknown

* Merge pull request #1 from banesullivan/patch-1

Add on_server_ready update callback for vtkLocalView ([`fbcabcd`](https://github.com/Kitware/trame-vtk/commit/fbcabcd38b7574483da669cc652ce2a01e68e9f8))


## v2.0.6 (2022-09-01)

### Chore

* chore(semantic-release): bump version to latest

Signed-off-by: Patrick Avery &lt;patrick.avery@kitware.com&gt; ([`ee2d58c`](https://github.com/Kitware/trame-vtk/commit/ee2d58c1c9ba50e704b74a088f90239530a06313))

### Documentation

* docs(coverage): remove codecov PR comment

Signed-off-by: Patrick Avery &lt;patrick.avery@kitware.com&gt; ([`5cce2fe`](https://github.com/Kitware/trame-vtk/commit/5cce2fe064625de02d6c590b65c925e31e0b36be))

* docs(coverage): add .coveragerc

Signed-off-by: Patrick Avery &lt;patrick.avery@kitware.com&gt; ([`6dd5e1d`](https://github.com/Kitware/trame-vtk/commit/6dd5e1d2ab44ff42ea5510db9aab736e49104b41))

* docs(ci): add coverage and codecov upload

Signed-off-by: Patrick Avery &lt;patrick.avery@kitware.com&gt; ([`b4d7c6e`](https://github.com/Kitware/trame-vtk/commit/b4d7c6ee53917e94ef0a9f5ae27db7cb8af430b6))

* docs(readme): add CI badge

Signed-off-by: Patrick Avery &lt;patrick.avery@kitware.com&gt; ([`214e1bf`](https://github.com/Kitware/trame-vtk/commit/214e1bfb4419a83c6390f1b8bf3cafa75fb3d1c7))

* docs(contributing): add CONTRIBUTING.rst

Signed-off-by: Patrick Avery &lt;patrick.avery@kitware.com&gt; ([`4bb579d`](https://github.com/Kitware/trame-vtk/commit/4bb579de9779b735f7517d5e47bff15dc6182066))

### Fix

* fix(VtkPiecewiseEditor): expose piecewise editor widget ([`1e44b6d`](https://github.com/Kitware/trame-vtk/commit/1e44b6d71f511d19dc95ee42e0d9c981258259b1))


## v2.0.5 (2022-06-01)

### Fix

* fix(paraview): replace invalid import path ([`bd33f2a`](https://github.com/Kitware/trame-vtk/commit/bd33f2a2c71f80792a3039271d70b32f100aeed0))


## v2.0.4 (2022-05-31)

### Fix

* fix(widgets): Expose more props ([`2fa0156`](https://github.com/Kitware/trame-vtk/commit/2fa01565461f62f96d3a18b2f649b5484981e5bf))


## v2.0.3 (2022-05-29)

### Fix

* fix(js): add trame-vtk.js before uploading to pypi

Signed-off-by: Patrick Avery &lt;patrick.avery@kitware.com&gt; ([`ec9b1f9`](https://github.com/Kitware/trame-vtk/commit/ec9b1f9e67f43618824459a2a7b6cfbf798dbf64))


## v2.0.2 (2022-05-27)

### Fix

* fix(paraview): remove unnecessary check for import

It is okay to check the servermanager import at the time of instantiating the Helper class, and we
do not need to check for the servermanager when the module is imported.

Signed-off-by: Patrick Avery &lt;patrick.avery@kitware.com&gt; ([`301b684`](https://github.com/Kitware/trame-vtk/commit/301b684378f30d46e93939da67ebd11f2027bf41))


## v2.0.1 (2022-05-27)

### Fix

* fix: add initial CI, including semantic release

Signed-off-by: Patrick Avery &lt;patrick.avery@kitware.com&gt; ([`2f72dda`](https://github.com/Kitware/trame-vtk/commit/2f72dda6bf851b8afea1f1cf34d616554b5b5dfc))

### Unknown

* trame-vtk brings widgets to support VTK or ParaView

Typically trame-vtk enable remote or local rendering from a vtkRenderWindow or a ParaView view proxy
This library is meant to be used with trame 2+ ([`77e7b70`](https://github.com/Kitware/trame-vtk/commit/77e7b701a9b3e58e316988dca6ee7981450f8caa))
