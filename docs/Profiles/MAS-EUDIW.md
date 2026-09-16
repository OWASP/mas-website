---
hide: toc
title: "MAS-EUDIW - EU Digital Identity Wallet"
---

The Netherlands joined forces with the OWASP MAS core team and worked to translate the applicable regulatory requirements into an OWASP MAS profile.

<center>
<img src="/assets/EUDIW%20Profile.png" style="width: 70%; border-radius: 5px" alt="OWASP MAS EUDI Wallet Profile - Requirements Catalogue and Practical Guidelines"/>
</center>

This work resulted in the **OWASP MAS EUDI Wallet Profile Requirements Catalogue**, which provides a list of requirements with which the EUDI Wallet Instance should comply, as well as a companion guide called the **OWASP MAS EUDI Wallet Profile Practical Guidelines**. The latter provides practical guidelines on applying these requirements and the OWASP MAS framework to **sensitive** and EUDI wallets.

The OWASP MAS EUDI Wallet Profile is currently being integrated into the Dutch national EUDI wallet certification scheme and the Dutch EUDIW Protection Profile.

This work was funded by the [Dutch EUDI-program](https://www.nldigitalgovernment.nl/overview/identity/id-wallet/) and built in collaboration between OWASP, MinBZK (NL), CCB (BE) and TRAFICOM (FI).

Learn more about the EU Digital Identity Wallet:

- [eudi.dev](https://eudi.dev/): the developer portal for the EU Digital Identity Wallet reference implementation.
- [EU Digital Identity Wallet Home](https://ec.europa.eu/digital-building-blocks/sites/spaces/EUDIGITALIDENTITYWALLET/pages/694487738/EU+Digital+Identity+Wallet+Home): the European Commission's Digital Building Blocks wiki for the EU Digital Identity Wallet.

## About the Profile

MAS-EUDIW draws on the large majority of the controls from all four existing MAS profiles and covers the assets unique to a digital identity system, such as **Wallet Instance Attestations (WIA)** and **Person Identification Data (PID)**.

The profile's requirements are mapped to the [**Risk Register for European Digital Identity Wallets**](https://eur-lex.europa.eu/eli/reg_impl/2024/2981/oj/eng), linking each technical control to the high-level risks, system-related risks, technical threats, and wallet-specific threat scenarios it is designed to mitigate, as well as to the corresponding [OWASP MASWE](../MASWE/index.md) weakness. This provides a bridge between high-level regulatory requirements (such as eIDAS) and low-level technical tests.

The profile is built around two supporting concepts, **Assets** and **Configurations**, which are applied generically across requirements. It is the responsibility of the profile's user (the developer, issuer, or auditor) to map the relevant assets (e.g. usage logs, PIN salt, WIA, critical private keys) to the appropriate requirements, and to set the applicable configuration values (e.g. approved cryptographic algorithms, minimum OS version) based on their risk tolerance and current technology standards.

MAS-EUDIW is recommended for:

- EUDI Wallet Instances that need to demonstrate resistance against attackers with a "high attack potential", a key regulatory requirement for Level of Assurance (LoA) High.
- Other High Assurance (HA) apps that can benefit from applying a subset of, or extending, the same requirement set.

## Documents

- [OWASP MAS EUDI Wallet Profile Requirements Catalogue](#): the full list of requirements the EUDI Wallet Instance should comply with, mapped to the Risk Register for European Digital Identity Wallets and to OWASP MASWE.
- [OWASP MAS EUDI Wallet Profile Practical Guidelines](#): a companion guide with practical guidance on applying the requirements and the OWASP MAS framework to sensitive and EUDI wallets.
