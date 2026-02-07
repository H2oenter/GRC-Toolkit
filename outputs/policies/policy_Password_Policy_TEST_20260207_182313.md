# PASSWORD POLICY

## 1. DOCUMENT CONTROL

**Policy Title:** Password Policy  
**Policy Number:** POL-SEC-001  
**Version:** 1.0  
**Effective Date:** December 15, 2024  
**Last Review Date:** December 15, 2024  
**Next Review Date:** December 15, 2025  
**Policy Owner:** Chief Information Security Officer (CISO)  
**Approved By:** Chief Executive Officer (CEO)

---

## 2. PURPOSE

This Password Policy establishes mandatory requirements for password creation, management, and protection across all TechCorp Inc systems and applications. This policy ensures the confidentiality, integrity, and availability of company information assets by implementing strong authentication controls that align with SOC 2 Type II requirements and industry best practices for financial technology organizations.

---

## 3. SCOPE

This policy applies to:
- All TechCorp Inc employees, contractors, consultants, and temporary staff
- All systems, applications, and services that require password authentication
- All company-owned, leased, or managed computing devices and systems
- All third-party systems and applications accessed using TechCorp credentials
- All privileged and non-privileged user accounts

**Exclusions:**
- System-generated passwords for automated processes (covered under separate technical standards)
- Emergency break-glass procedures (covered under Incident Response Policy POL-SEC-005)

---

## 4. DEFINITIONS

**Authentication Factor:** A piece of information used to verify a user's identity, categorized as something you know (password), something you have (token), or something you are (biometric).

**Brute Force Attack:** An automated attempt to gain unauthorized access by systematically trying multiple password combinations.

**Dictionary Attack:** A method of breaking into password-protected systems by systematically entering every word in a dictionary as a password.

**Multi-Factor Authentication (MFA):** An authentication method requiring two or more independent credentials from different authentication factor categories.

**Passphrase:** A sequence of words or text used as a password, typically longer than traditional passwords and easier to remember.

**Password Complexity:** Requirements for password composition including character types, length, and structure.

**Password Entropy:** A measure of password strength based on the unpredictability and randomness of the password.

**Privileged Account:** User accounts with elevated permissions that can access sensitive systems, modify security settings, or perform administrative functions.

**Single Sign-On (SSO):** An authentication process allowing users to access multiple applications with one set of login credentials.

---

## 5. POLICY STATEMENTS

### 5.1 Password Composition Requirements

5.1.1 All user passwords must be a minimum of 12 characters in length for standard user accounts and 16 characters for privileged accounts.

5.1.2 Passwords must contain at least three of the following four character types:
- Uppercase letters (A-Z)
- Lowercase letters (a-z)
- Numbers (0-9)
- Special characters (!@#$%^&*()_+-=[]{}|;:,.<>?)

5.1.3 Passwords must not contain:
- The user's account name, display name, or parts of their full name
- Company name "TechCorp" or common variations
- Dictionary words in any language
- Common keyboard patterns (qwerty, 123456, etc.)
- Previously used passwords from the last 12 password changes

5.1.4 Passphrases of 20 characters or more containing spaces and multiple words are acceptable alternatives to complex passwords, provided they meet entropy requirements.

### 5.2 Password Management and Storage

5.2.1 All employees must use TechCorp-approved password managers for storing and generating passwords for non-SSO systems.

5.2.2 Passwords must never be stored in plain text format in any system, document, or communication.

5.2.3 Shared passwords for system accounts are prohibited; each user must have unique credentials.

5.2.4 Default passwords on all systems and applications must be changed immediately upon installation or first use.

5.2.5 Passwords must not be shared, disclosed, or transmitted via email, instant messaging, or any unencrypted communication method.

### 5.3 Password Expiration and Rotation

5.3.1 Standard user account passwords must be changed every 90 days maximum.

5.3.2 Privileged account passwords must be changed every 60 days maximum.

5.3.3 Service account passwords must be changed every 180 days maximum or immediately upon personnel changes affecting account access.

5.3.4 Passwords must be changed immediately when:
- There is suspected or confirmed compromise
- An employee with knowledge of the password leaves the organization
- The password has been shared inappropriately
- Required by incident response procedures

### 5.4 Multi-Factor Authentication Requirements

5.4.1 Multi-Factor Authentication (MFA) is mandatory for:
- All Okta SSO access
- All privileged accounts
- All remote access to company systems
- All access to financial and payment processing systems
- All administrative interfaces

5.4.2 MFA must use time-based one-time passwords (TOTP) or hardware tokens; SMS-based authentication is prohibited for privileged access.

5.4.3 MFA backup codes must be stored securely and never shared between users.

### 5.5 Account Lockout and Security Controls

5.5.1 User accounts must be automatically locked after 5 consecutive failed login attempts within a 15-minute period.

5.5.2 Locked accounts must remain locked for a minimum of 15 minutes or until manually unlocked by IT administration.

5.5.3 All password authentication attempts must be logged and monitored for suspicious activity.

5.5.4 Automated password attack detection must trigger immediate security alerts to the SOC team.

### 5.6 Single Sign-On (SSO) Requirements

5.6.1 All employees must use Okta SSO for accessing approved business applications where technically feasible.

5.6.2 Direct application passwords are prohibited for SSO-enabled systems except for emergency access procedures.

5.6.3 SSO session timeouts must not exceed 8 hours for standard users and 4 hours for privileged users.

5.6.4 SSO sessions must be terminated immediately upon user logout or system inactivity exceeding 30 minutes.

### 5.7 Emergency and Break-Glass Access

5.7.1 Emergency access accounts must have unique, complex passwords stored in a secured, auditable system accessible only to authorized personnel.

5.7.2 Emergency password usage must be logged, reviewed, and reported to the CISO within 24 hours.

5.7.3 Emergency passwords must be changed within 24 hours of use.

---

## 6. ROLES AND RESPONSIBILITIES

### Executive Leadership
- Provide resources and support for password policy implementation
- Ensure policy compliance is included in performance evaluations
- Approve policy exceptions and waivers

### Chief Information Security Officer (CISO)
- Oversee policy implementation and enforcement
- Review and approve password policy exceptions
- Ensure compliance monitoring and reporting
- Coordinate with legal and compliance teams on regulatory requirements

### IT Security Team
- Implement technical controls to enforce password requirements
- Monitor password-related security events and incidents
- Conduct regular password security assessments
- Maintain and update password management tools

### IT Department
- Configure systems to enforce password policy requirements
- Provide technical support for password-related issues
- Implement and maintain Okta SSO infrastructure
- Assist with password reset procedures

### Department Managers
- Ensure team members understand and comply with password requirements
- Report suspected password policy violations
- Support password security training initiatives
- Approve business justifications for policy exceptions

### All Employees
- Create and maintain passwords according to policy requirements
- Use approved password managers for credential storage
- Report suspected password compromises immediately
- Complete mandatory password security training

### Third Parties and Contractors
- Comply with all password requirements when accessing TechCorp systems
- Use only approved authentication methods
- Report security incidents involving TechCorp credentials

---

## 7. ENFORCEMENT AND COMPLIANCE

### Compliance Measurement
- Monthly automated password policy compliance reports
- Quarterly password strength assessments using approved tools
- Annual penetration testing including password attack simulations
- Continuous monitoring of authentication logs for policy violations

### Consequences of Non-Compliance
- **First Violation:** Mandatory security awareness training and written warning
- **Second Violation:** Formal disciplinary action and additional training requirements
- **Third Violation:** Suspension of system access pending review
- **Severe Violations:** Immediate termination and potential legal action

### Exception and Waiver Process
- All exceptions must be requested in writing with business justification
- CISO approval required for all exceptions
- Exceptions must include compensating controls and risk mitigation measures
- Maximum exception period of 90 days with mandatory review
- All exceptions must be documented and tracked in the GRC system

---

## 8. RELATED DOCUMENTS

- **POL-SEC-002:** Multi-Factor Authentication Policy
- **POL-SEC-003:** Access Control Policy  
- **POL-SEC-004:** Information Security Awareness Training Policy
- **POL-SEC-005:** Incident Response Policy
- **STD-SEC-001:** Password Technical Implementation Standards
- **PROC-SEC-001:** Password Reset Procedures
- **PROC-SEC-002:** Account Provisioning and Deprovisioning Procedures
- **SOC 2 Type II Control Documentation**
- **NIST Cybersecurity Framework Implementation Guide**

---

## 9. REVISION HISTORY

| Version | Date | Author | Description of Changes |
|---------|------|--------|----------------------|
| 1.0 | December 15, 2024 | CISO Office | Initial policy creation and approval |

---

**Document Classification:** Internal Use Only  
**Next Scheduled Review:** December 15, 2025  
**Policy Distribution:** All TechCorp Inc Personnel via Company Intranet