---
hide: toc
title: "MAS-L2 - Advanced Security"
---

MAS-L2 extends [MAS-L1](MAS-L1.md), introducing additional security measures and best practices for mobile apps to address **advanced threats** requiring more rigorous threat modeling and testing strategies.

It assumes that:

- the **security controls of the mobile operating system** cannot be trusted (e.g. the device is rooted/jailbroken).
- the **primary user of the device** is not viewed as an adversary.
- **other applications** installed on the device are viewed as an adversary.
- a **third party with or without physical access** is viewed as an adversary.

MAS-L2 is recommended for

- apps that handle **high-risk sensitive data** and **contain sensitive functionality**

For example:

- **Health care apps** that store or process sensitive health or personally identifiable information which could be used for identity theft, fraudulent claims, discrimination, or other forms of abuse. Depending on the jurisdiction and type of application, relevant regulatory and compliance frameworks include the [HIPAA Privacy, Security, Breach Notification, and Patient Safety Rules](https://www.hhs.gov/hipaa/for-professionals/index.html) in the US, the [European Health Data Space (EHDS)](https://eur-lex.europa.eu/legal-content/EN/ALL/?uri=CELEX%3A32025R0327) and applicable [medical device regulations](https://health.ec.europa.eu/medical-devices-sector/new-regulations_en) in the EU, the [DiGAV requirements for digital health applications](https://www.gesetze-im-internet.de/digav/) in Germany, and the [NHS Digital Technology Assessment Criteria (DTAC)](https://digitalregulations.innovation.nhs.uk/regulations-and-guidance-for-developers/all-developers-guidance/using-the-digital-technology-assessment-criteria-dtac/) and applicable [medical device regulations for software and apps](https://www.gov.uk/government/publications/medical-devices-software-applications-apps) in the UK.
- **Financial apps** that provide access to sensitive information such as credit card numbers or that let the user move funds. These apps warrant additional controls to prevent fraud and typically need to demonstrate compliance with standards and regulations such as PCI DSS, the Gramm-Leach-Bliley Act, and the Sarbanes-Oxley Act.
