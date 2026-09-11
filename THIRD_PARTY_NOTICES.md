# Third-Party Notices

Last updated: September 11, 2026

SMS Gateway OSS is licensed under the MIT License. That license applies only to the original project code and assets owned by this project’s contributors. Third-party software remains subject to its own copyright notices and license terms.

This document identifies the primary third-party software used to build or run the project. It is not a replacement for the complete license text supplied by each dependency.

## Runtime and Packaged Components

| Component | Purpose | License |
|---|---|---|
| CPython | Python runtime packaged for Android | Python Software Foundation License |
| Flask | Local dashboard and HTTP API framework | BSD 3-Clause |
| Werkzeug | WSGI and HTTP utilities used by Flask | BSD 3-Clause |
| Jinja | HTML template rendering used by Flask | BSD 3-Clause |
| ItsDangerous | Flask signing and serialization dependency | BSD 3-Clause |
| Click | Flask command-line dependency | BSD 3-Clause |
| Blinker | Flask signaling dependency | MIT |
| MarkupSafe | Escaping support used by Jinja | BSD 3-Clause |
| PyJNIus | Python-to-Java bridge used for Android APIs | MIT |
| Dropbear SSH | SSH client and key-generation tools used for the reverse tunnel | Dropbear permissive license; see the bundled upstream license text |
| LibTomCrypt | Cryptographic library used by Dropbear | LibTom public-domain dedication / Unlicense-style terms |
| LibTomMath | Multiple-precision mathematics library used by Dropbear | LibTom public-domain dedication / Unlicense-style terms |

## Build-Time Components

The following tools are used to produce the Android package but are not necessarily distributed as standalone components inside the APK:

| Component | Purpose | License |
|---|---|---|
| Buildozer | Android build orchestration | MIT |
| python-for-android | Packages Python applications for Android | MIT |
| Cython | Compiles Python and Cython modules used by the Android build | Apache License 2.0 |
| Android SDK | Android application build tools and platform APIs | Subject to Google’s Android SDK terms |
| Android NDK | Native Android compiler toolchain | Subject to the licenses included with the NDK distribution |
| OpenJDK | Java toolchain used during the Android build | GNU GPL v2 with Classpath Exception and related component licenses |
| Gradle and Android Gradle Plugin | Android build automation | Subject to their respective licenses |

## External Services

The following services are referenced by the project but are not included in the source code or APK:

- **Pinggy** provides the optional public reverse-tunnel endpoint. Its use is governed by Pinggy’s own terms, acceptable-use policy, limits, and privacy policy.
- **Google Colab** can be used as an online build environment. Its use is governed by Google’s applicable terms and policies.
- **GitHub Actions** can be used for continuous integration and APK builds. Its use is governed by GitHub’s applicable terms and policies.

## License Files

Where practical, complete third-party license texts should be stored under:

```text
third_party/licenses/
```

The Dropbear build script copies the upstream Dropbear license into that directory. Release maintainers should also collect the license files for the exact Python packages and native components included in each release.

## Release-Maintainer Responsibilities

Before publishing a source archive or APK release:

1. Generate the release from a clean checkout.
2. Record the exact dependency versions used by the build.
3. Review all direct and transitive dependency licenses.
4. Include required copyright, attribution, and license notices.
5. Update this document when a dependency is added, removed, replaced, or relicensed.
6. Preserve third-party notices in source and binary distributions where required.
7. Do not assume that the project’s MIT License overrides a third-party license.

## No Endorsement

The names and trademarks of third-party projects and service providers belong to their respective owners. Their inclusion does not imply endorsement of SMS Gateway OSS, and this project does not claim endorsement of those third parties.

## Corrections

If a component or license is missing or incorrectly identified, please open a documentation issue. Do not use a public issue to disclose a security vulnerability; follow `SECURITY.md` instead.
