# MAS-L1 - Essential Security

MAS-L1 provides a baseline for the most fundamental security requirements and best practices that every mobile app should meet to protect against **common threats**.

This profile emphasizes adhering to secure defaults provided by the OS and frameworks and implementing well-recognized security measures considered 'essential'. These include, for example, using TLS or up-to-date strong cryptography. Certain tests are included due to their minimal implementation effort relative to their significant security enhancement.

It assumes that:

- the **security controls of the mobile operating system** can be trusted (e.g. the device is not rooted/jailbroken).
- the **primary user of the device** is not viewed as an adversary.
- **other applications** installed on the device are viewed as an adversary.

MAS-L1 is recommended for

- all mobile apps as a baseline
- apps that only deal with (user) **low-risk sensitive data** and do **not contain sensitive functionality**.
