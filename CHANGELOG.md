# CHANGELOG

<!-- version list -->

## v1.7.0 (2026-11-13)

### Bug Fixes

- Harden office document previews and share route error handling
  ([`ed1669c`](https://github.com/ICIJ/datashare-preview/commit/ed1669cfcf247b234566b527ba9ad461770b741a))

- Reject office documents libreoffice cannot convert
  ([`38f0a18`](https://github.com/ICIJ/datashare-preview/commit/38f0a1881516c93cfec6342d0f7c6928ca7e46a7))

- Reject thumbnails libreoffice cannot convert
  ([`a2d6123`](https://github.com/ICIJ/datashare-preview/commit/a2d61235db2a366bfdf245f143e9c0dbd40b6e5c))

- **ci**: Install system dependencies with apt-get again
  ([`c7c3002`](https://github.com/ICIJ/datashare-preview/commit/c7c3002e62fb03be37a2bfe84885acd6923cc1c2))

### Chores

- **ci**: Test oldest and newest python only, cache apt packages
  ([`8d4b9e0`](https://github.com/ICIJ/datashare-preview/commit/8d4b9e002e74323335fe522ad91154027504e65b))

### Documentation

- Add design for office documents pdf route
  ([`96aa8d3`](https://github.com/ICIJ/datashare-preview/commit/96aa8d358ba541559ce89e139f29aac4e291fbc8))

- Add implementation plan for office documents pdf route
  ([`5723473`](https://github.com/ICIJ/datashare-preview/commit/57234732cb6788fe39ea0732eb437848e43d4060))

### Features

- Preview common office documents
  ([`5c9f100`](https://github.com/ICIJ/datashare-preview/commit/5c9f1004783002b7493b457567ef9b590e67fe3e))

- Serve office documents as pdf
  ([`55bbb5f`](https://github.com/ICIJ/datashare-preview/commit/55bbb5f4be411eb6744c59bb746c68d1f882b296))

- **preview**: Support office documents, spreadsheet templates and more image types
  ([`856edfa`](https://github.com/ICIJ/datashare-preview/commit/856edfa99decf50a88c18d9ffc5746b476842708))


## v1.6.4 (2026-11-13)

### Bug Fixes

- **ci**: Release only the commit ci tested, with the official semantic-release action
  ([`ba2a899`](https://github.com/ICIJ/datashare-preview/commit/ba2a89987c97ab510e42ad95ad35664cbca7445d))

- **document**: Pass content type when guessing a file extension
  ([`899de67`](https://github.com/ICIJ/datashare-preview/commit/899de67cf3cb7e7b3c104087feddd04ae85441d9))

- **document**: Reject identifiers that escape the cache directory
  ([`7f2fa94`](https://github.com/ICIJ/datashare-preview/commit/7f2fa94f331c7b67b0b20de3cb10edb8d6424696))

- **document**: Stream downloads with a size limit and a timeout
  ([`2c998b0`](https://github.com/ICIJ/datashare-preview/commit/2c998b0d1f061b3211e670c2295df4a425cae349))

- **main**: Generate previews in a thread pool
  ([`5f2fe7f`](https://github.com/ICIJ/datashare-preview/commit/5f2fe7f3f02ff30f79bf94a8044d8e5e60d64590))

- **main**: Validate page and cap thumbnail size
  ([`44635d3`](https://github.com/ICIJ/datashare-preview/commit/44635d3ba6d42fc8cb971e90964a4405a05a2d82))

- **spreadsheet**: Stop ssconvert after a timeout
  ([`efe82fd`](https://github.com/ICIJ/datashare-preview/commit/efe82fde4ef858dda936b519ffe0382584dc6a21))

### Chores

- Remove unused setup.py
  ([`9b3e3e7`](https://github.com/ICIJ/datashare-preview/commit/9b3e3e73eca88d7bae42d12a12c8f7adbe4eee9d))

- **ci**: Release and publish to docker hub on green main
  ([`394a750`](https://github.com/ICIJ/datashare-preview/commit/394a7502f46ddd053a3e2cfe2e919050ff141860))

- **ci**: Test on python 3.15 and bump github actions
  ([`1844041`](https://github.com/ICIJ/datashare-preview/commit/1844041c47bf40b8c358f2503763d8cb7676ce5c))

- **deps**: Move project metadata to the pep 621 section and use httpx2 in tests
  ([`6590206`](https://github.com/ICIJ/datashare-preview/commit/65902060371a6a028e10d77a23eb37d735525cfe))

- **deps**: Move pytest to dev dependencies and drop broken uvicorn extra
  ([`f6f1a2b`](https://github.com/ICIJ/datashare-preview/commit/f6f1a2b221bf6eab96cb2fa928fa7a9de9fc0226))

- **deps**: Upgrade python dependencies and require python 3.11
  ([`f034c63`](https://github.com/ICIJ/datashare-preview/commit/f034c636accf7da1d0f7a9ba56e8e73d02faba34))

- **docker**: Use python 3.15 on debian trixie and exiftool 13.63
  ([`339daf8`](https://github.com/ICIJ/datashare-preview/commit/339daf8bd27bc08684a3c4a90b717305f7c19bf1))

### Documentation

- Convert readme to markdown and document automated releases
  ([`41591df`](https://github.com/ICIJ/datashare-preview/commit/41591df047b8b7c35995990930599030a8f27926))

### Refactoring

- Remove unused helpers and duplicate content type property
  ([`d05fbc2`](https://github.com/ICIJ/datashare-preview/commit/d05fbc23ff0721f7b6a222b9fbbd0ec7f5e17709))


## v1.6.3 (2025-10-17)

### Bug Fixes

- Typo
  ([`5ae77fc`](https://github.com/ICIJ/datashare-preview/commit/5ae77fc4ba2863dfe6b897900ad3a5ba818cae56))

### Chores

- Update pytest to 8.4.2
  ([`e8ec3f0`](https://github.com/ICIJ/datashare-preview/commit/e8ec3f06ac87a59db5b4d2585c8b807644d6981b))


## v1.6.2 (2025-10-17)

### Bug Fixes

- Reimplement config compatible with Pydantic v2
  ([`5d1ab90`](https://github.com/ICIJ/datashare-preview/commit/5d1ab90a2382802ed09eac1da9253db0bdc7dce8))

### Build System

- Add .git and Dockerfile to dockerignore
  ([`f232c78`](https://github.com/ICIJ/datashare-preview/commit/f232c782e04bcd6ea38a813e2e84d5f82367f206))

- Use python 3.13 in Docker
  ([`ba19812`](https://github.com/ICIJ/datashare-preview/commit/ba1981224343851abdfa8af872722489d1825eb0))

### Features

- Move cookies to client
  ([`68fbeb7`](https://github.com/ICIJ/datashare-preview/commit/68fbeb7cfe9425d7c6874b7b188fa62128f654d9))

- Use env var to configure CMD
  ([`fc90200`](https://github.com/ICIJ/datashare-preview/commit/fc90200324873ec57272ffb2f22d525df2917443))


## v1.6.1 (2025-10-16)

### Build System

- Import version from package
  ([`4ceb5a1`](https://github.com/ICIJ/datashare-preview/commit/4ceb5a14ba69293d48bb0644421a6adf6bf0fae6))

### Features

- Add more supported images
  ([`a3c4483`](https://github.com/ICIJ/datashare-preview/commit/a3c4483f522ae0b2656b1208c37a4e80bff529ea))


## v1.6.0 (2025-10-16)

### Bug Fixes

- Correct ENV variable syntax in Dockerfile
  ([`64e811f`](https://github.com/ICIJ/datashare-preview/commit/64e811f4015ebfbbe820b7208a9b5971de60868b))

- Ensure we support DNG with dcraw
  ([`6e77391`](https://github.com/ICIJ/datashare-preview/commit/6e77391304abf01c67cb301e40f1f2ebf2aa159e))

### Build System

- Add os deps to make install
  ([`0d96b40`](https://github.com/ICIJ/datashare-preview/commit/0d96b409248950c931485aaffb26964f1801170e))

- Migrate to python 3.14
  ([`08a0a8a`](https://github.com/ICIJ/datashare-preview/commit/08a0a8a296dc7c5320cdf388899390f7e0e47fa4))

### Chores

- Refresh dependencies
  ([`2a2049b`](https://github.com/ICIJ/datashare-preview/commit/2a2049b96bdedf5eba91ed26ac93811589964adc))

- Upgrade to pydantic v2
  ([`f18e27f`](https://github.com/ICIJ/datashare-preview/commit/f18e27f423b3c15b97102d1b10f3fa2ea42bbfcd))

### Continuous Integration

- Upgrade to python 11 to 14
  ([`fef6657`](https://github.com/ICIJ/datashare-preview/commit/fef66575dcc53b45686701f90ec43180d7c8d2da))

- Use make to install os deps
  ([`e5bb479`](https://github.com/ICIJ/datashare-preview/commit/e5bb4794f6fd04968e5073e4c2507b08a27a36b2))

### Features

- Add setup tools
  ([`714bc7b`](https://github.com/ICIJ/datashare-preview/commit/714bc7b979000466c1727385dfb0968f8fbcb036))

- Add var to specify HOST and PORT
  ([`00d8a32`](https://github.com/ICIJ/datashare-preview/commit/00d8a323bc9dccee102eb76fb3939a72a220502a))

- Catch unauthorized
  ([`58b5047`](https://github.com/ICIJ/datashare-preview/commit/58b5047a96a494c8b3ecbaa266330fd7e3fb10fc))

- Migrate to fastapi lifespan and response model
  ([`26fcbb6`](https://github.com/ICIJ/datashare-preview/commit/26fcbb6433cbabbec4313f0bfb4aac420bb249cd))

### Refactoring

- Remove depracted version
  ([`39c9d51`](https://github.com/ICIJ/datashare-preview/commit/39c9d5161417ab4d983a20abc0ba94c86d8021fd))

- Remove fix for ghostscript
  ([`e46f522`](https://github.com/ICIJ/datashare-preview/commit/e46f522d239b6f3515432d7b51a304f3967f6ed3))

- Sort makefile targets
  ([`74351cc`](https://github.com/ICIJ/datashare-preview/commit/74351ccf98b1cad8aa29e8d5af6f8d26571df5e1))


## v1.5.3 (2023-10-06)

### Features

- Change http code to 4xx
  ([`b4c0cba`](https://github.com/ICIJ/datashare-preview/commit/b4c0cba6d1498fb0ca410d4ae425151074b8461d))

- Update http code with 4xx
  ([`7869d4c`](https://github.com/ICIJ/datashare-preview/commit/7869d4c6489d425343fe2b2c1108e475b431d1f3))


## v1.5.1 (2023-10-06)

### Build System

- Add .dockerignore
  ([`9185b7b`](https://github.com/ICIJ/datashare-preview/commit/9185b7ba79f5fa543bb5cd03e72ae18e229ecf9d))

- Add .github to dockerignore
  ([`dfcf4aa`](https://github.com/ICIJ/datashare-preview/commit/dfcf4aa51319b2bcfa83d426ea5b20a6f8a6a94d))

- Remove thread limits
  ([`7b2b7e4`](https://github.com/ICIJ/datashare-preview/commit/7b2b7e4569ce756a015a45aa3167bf3cc5a7878d))

- Use debian bullseye and export requirements in stage
  ([`dfad565`](https://github.com/ICIJ/datashare-preview/commit/dfad56529cba7baa5f618c4c0ad980e41be1078a))

### Continuous Integration

- Build for python 3.11
  ([`f62c3e2`](https://github.com/ICIJ/datashare-preview/commit/f62c3e21dda88176ba71e418b81a0891c2cc1944))

- Remove circleci
  ([`0ee5f8a`](https://github.com/ICIJ/datashare-preview/commit/0ee5f8ac5e5dc8b3d38417f0563c89f0f555219a))

- Setup github actions
  ([`432d384`](https://github.com/ICIJ/datashare-preview/commit/432d38492da1f7a350ac5d1d530947bc49c353da))

### Features

- Delete target file when it's too big
  ([`177c8b5`](https://github.com/ICIJ/datashare-preview/commit/177c8b54143d0e19d104633218190dafd6de6e17))

- Handle more error
  ([`5a14718`](https://github.com/ICIJ/datashare-preview/commit/5a147180eaa3ad0532a34f653aed53d9fb978df9))

- Restore async requests
  ([`ddbc532`](https://github.com/ICIJ/datashare-preview/commit/ddbc53288268428b52474d9cd1576051055db032))


## v1.4.10 (2023-10-05)

### Build System

- At least 2 threads for magic
  ([`7e44c3a`](https://github.com/ICIJ/datashare-preview/commit/7e44c3a55b74ea21581794cc0d07a4b6acd7c446))


## v1.4.9 (2023-10-05)

### Build System

- Only limit threads with Magick
  ([`09de012`](https://github.com/ICIJ/datashare-preview/commit/09de01213bd4da4c58cab8f3799becd724bbef63))


## v1.4.8 (2023-10-05)

### Build System

- Thread limit on ImageMagick
  ([`ac92168`](https://github.com/ICIJ/datashare-preview/commit/ac92168c012a72f145e9334d3c553a596032cf86))


## v1.4.7 (2023-10-05)

### Chores

- Restore latest verions of packages
  ([`4a26c63`](https://github.com/ICIJ/datashare-preview/commit/4a26c635dbe8e9e8ccc25b9b39eb11639ea49712))

### Features

- Use sync httpx
  ([`ba5932a`](https://github.com/ICIJ/datashare-preview/commit/ba5932a07e6b9f73959cc5b781d5edd5e9fc5d98))


## v1.4.6 (2023-10-04)

### Chores

- Downgrade more deps
  ([`08a4fb9`](https://github.com/ICIJ/datashare-preview/commit/08a4fb9086cdb508cae1c70fac5a3ac4390b2a47))


## v1.4.5 (2023-10-04)

### Chores

- Downgrade uvicorn
  ([`fb50c1f`](https://github.com/ICIJ/datashare-preview/commit/fb50c1f5394e9a2be70076538f9500bbda395259))


## v1.4.4 (2023-10-04)

### Chores

- Downgrade to httpcore 0.16.3 and httpx 0.23.3
  ([`c0618c7`](https://github.com/ICIJ/datashare-preview/commit/c0618c715535bac41416477c120ad4efd8555386))


## v1.4.3 (2023-10-04)

### Chores

- Rollbacl anyio to 3.6.2
  ([`09ea680`](https://github.com/ICIJ/datashare-preview/commit/09ea680c41658f94872361e23e699b0825953230))


## v1.4.2 (2023-10-04)

### Chores

- Downgrade anyio
  ([`a691530`](https://github.com/ICIJ/datashare-preview/commit/a6915305346393e2e8b3108edb955590d0a8aca9))


## v1.4.1 (2023-10-04)

### Chores

- Upgrade uvicorn and httpx
  ([`9e9bd3e`](https://github.com/ICIJ/datashare-preview/commit/9e9bd3ecd06e069d8c079372e9a9a122acf0e790))


## v1.4.0 (2023-10-04)

### Build System

- Add packages option
  ([`1680a5f`](https://github.com/ICIJ/datashare-preview/commit/1680a5f8092149e7be84606a75c8243e5dcce67b))

- Add support for multi arch Docker image
  ([`f4df142`](https://github.com/ICIJ/datashare-preview/commit/f4df1423f068b558d5d3b235c0371a4f29c2e4a4))

- Fix typo
  ([`6a65364`](https://github.com/ICIJ/datashare-preview/commit/6a65364d8cd0f6cf9a8c0a6c54cead6596694689))

### Features

- Add docstring and type hint
  ([`d5b754a`](https://github.com/ICIJ/datashare-preview/commit/d5b754a08eb95e8e6fccb3fbc8f30c3ef1bc4fcf))

- Catch DocumentRootTooBig error
  ([`2188745`](https://github.com/ICIJ/datashare-preview/commit/2188745530c7363aee9e73d0718377374ab1c878))

- Load root and test its size
  ([`fc56b9c`](https://github.com/ICIJ/datashare-preview/commit/fc56b9c5d5473a8bf7545bc65756d45301bf4302))

### Testing

- Add new helper to build document url
  ([`c9e3aad`](https://github.com/ICIJ/datashare-preview/commit/c9e3aad88816e0cbdc45ef45f68a7e90e6b61d2c))


## v1.1.2 (2022-12-16)


## v1.1.1 (2022-12-16)

- Initial Release
