# Security policy

This is local educational software with a dependency-free runtime core. It does
not download input, execute supplied code, access credentials or send data over
the network. The JSON CLI limits actual input bytes and matrix dimensions;
these limits do not establish a security certification or a performance SLA.

Report exploitable concerns through GitHub's private vulnerability reporting
when enabled, or email **support@quantchapter.com** with subject
`Linear Algebra Lab security report`. Include the affected version, impact,
reproduction steps and a minimal constructed input. Do not send credentials,
personal data or executable attachments. Discuss disclosure privately before
opening a public issue containing exploit details.

Only the latest `0.1.x` release is maintained, on a best-effort basis. There is
no guaranteed response time, paid support agreement or bounty. Earlier versions
remain available for reproducibility without separate maintenance commitments.
Incorrect numerical results belong in an ordinary issue unless they also create
a security risk. Documented pivot rejection and floating-point limits are
explicit restrictions rather than promises to solve every supplied system.

Maintainers should review advisories and dependency updates, pin workflow actions,
limit ordinary CI tokens to read access and never execute contributor code with
release credentials. Enable secret scanning, push protection, dependency alerts
and private reporting where available. Repository files alone do not prove those
remote settings are enabled. Publish an advisory when a confirmed issue warrants it.
