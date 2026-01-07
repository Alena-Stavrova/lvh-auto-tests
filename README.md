# 🚀 E-commerce Test Automation Framework

**Python + Selenium framework for automated smoke and regression testing of international e-commerce platforms**

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/)
[![Selenium](https://img.shields.io/badge/Selenium-4.0+-green.svg)](https://www.selenium.dev/)

## 📋 Overview
This framework automates critical user flows for a single-brand e-commerce platform with 7+ localized websites. It handles complex business logic including country-specific payment/delivery options and dynamic product selection.

## ✨ Key Features
- **Multi-country support:** BG, CZ, DE, ES, EU, HU and IT variants
- **Intelligent test data:** Random product selection with price validation
- **Complex business logic:** Handles free shipping thresholds, payment/delivery dependencies
- **Real-world simulation:** Mimics actual user behavior end-to-end
- **Extensible architecture:** Easy to add new countries or test scenarios

## 🏗 Project Structure
lvh-auto-tests/
├── BG_order_V1.py # Bulgaria website automation
├── CZ_order_V1.py # Czech Republic website automation
├── DE_order_V1.py # Germany website automation
├── ES_order_V1.py # Spain website automation
├── EU_order_V1.py # European website automation
├── HU_order_V1.py # Hungary website automation
├── IT_order_V1.py # Italy website automation
├── requirements.txt # Dependencies
└── README.md # This file

## 🛠 Development Approach
This project represents a **collaborative development effort** where I served as the **technical lead and product owner**. My contributions include:

- **Architecture & Design:** Designed the overall test framework structure and flow logic
- **Requirements Specification:** Defined detailed test scenarios for 7 country-specific websites
- **Implementation & Debugging:** Wrote initial code, debugged complex issues, and adapted solutions
- **Business Logic Integration:** Implemented country-specific payment/delivery rules
- **Code Review & Quality:** Ensured code maintainability and adherence to Python best practices

**Tool Stack:** Python, Selenium, Git, and **AI-assisted development tools** (for code generation and optimization).

This approach allowed me to **accelerate development** while maintaining focus on solving complex testing challenges rather than boilerplate code.

## ⚙️ Prerequisites & Notes
- **Python 3.9+** and pip installed
- **ChromeDriver** compatible with your Chrome version
- **VPN connection required** for accessing some European websites from Russia
- Test data (phone numbers, emails) has been **sanitized** for public sharing

## 🚀 Getting Started
1. Clone repository: `git clone https://github.com/Alena-Stavrova/lvh-auto-tests.git`
2. Install dependencies: `pip install -r requirements.txt`
3. Ensure VPN is active for European websites
4. Run a test: `python DE_order_V1.py`

## 📈 Business Impact
- **Time savings:** Automates previously manual daily smoke testing
- **Risk reduction:** Ensures critical purchase flows work across all markets
- **Scalability:** Framework supports adding new countries in hours vs. days

## 🔄 Project Status & Future Improvements
This is a **living project** that I actively maintain and improve. Recent updates include:
- Performance optimizations for slow-running scripts
- Enhanced error handling 
- Added structured summary (order #, selected payment/delivery options)

**Planned improvements:**
- Adding summary to all scripts
- Improving speed if needed
- Adapting the scripts to test ANY existing flow based on the user's input 

## 🔗 Connect
- **My QA Portfolio & Resume:** [GitHub](https://github.com/Alena-Stavrova/qa-cv-portfolio)
- **Popular Article About My QA Journey:** [Habr](https://habr.com/ru/articles/853856/)
- **Email:** alenastavrova@gmail.com
