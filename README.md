<p align="center">
  <img src="resources/banner.png" alt="PunchedN banner" width="100%" />
</p>

<h3 align="center">Shift Management on Autopilot</h3>
 
<p align="center">
  <a href="LICENSE"><img alt="GitHub License" src="https://img.shields.io/github/license/isaac987/punchedn"></a>
  <!-- <a href="#"><img src="https://img.shields.io/badge/build-passing-brightgreen.svg" alt="Build Status"></a> -->
  <!-- <a href="#"><img src="https://img.shields.io/badge/version-0.1.0-orange.svg" alt="Version"></a> -->
  <img alt="GitHub contributors" src="https://img.shields.io/github/contributors/isaac987/punchedn">
  <a href="https://github.com/Isaac987/punchedn/pulls"><img alt="GitHub Issues or Pull Requests" src="https://img.shields.io/github/issues-pr/isaac987/punchedn"></a>
  <a href="https://discord.gg/2bgWhtCHbb"><img alt="Discord" src="https://img.shields.io/discord/1526075110543462410"></a>
</p>

Tired of manually scheduling your employees? Cluttering your camera roll with pictures of your schedule?

**PunchedN is the solution!** PunchedN is an employee schedule manager that automatically generates the best schedules for your employees. Not only that, PunchedN facilitates sick time and time-off management, and automatically handles shift changes. PunchedN is the easiest way to keep your team scheduled and in sync.

**PunchedN** automates the tedious parts of shift scheduling (conflict detection, availability tracking, and shift swaps), while giving buisness owners full control over branding, permissions, and integrations.

**The price is right!** You can setup **PunchedN** all on your own and have access to all of the time-saving features. However, if you prefer to skip the technical steps, we highly recommend our [fully managed setup and maintenance plans](#) so you can stay focused on running your business.


## Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Demo](#demo)
- [Installation](#installation)
- [Usage](#usage)
- [Configuration](#configuration)
- [Roadmap](#roadmap)
- [Contributing](#contributing)
- [Testing](#testing)
- [License](#license)
- [Acknowledgments](#acknowledgments)


## Features

**PunchedN** provides an extensive set of features for employees, managers, and buisness owners.

- **Automation Engine:** algorithm-driven schedule generation and templating with built-in overlap protection.
- **Workforce Tools:** self-service web and mobile interfaces for employees to manage availability, swap shifts, and request time off.
- **Platform Controls:** granular permission systems, custom white-labeling, and seamless integrations with external accounting software.  
- **Business Analytics:** actionable insights tracking sick leave patterns, overtime minimization, and automated compliance for restricted worker hours.
- **Hardware Integrations:** network support for physical time clocks utilizing NFC, RFID, and biometric scanners for secure clock-ins.

<!-- TODO: Have all of these link to documentation -->
| Admin                    | Manager                                             | HR                                | Employee                            |
| ------------------------ | --------------------------------------------------- | --------------------------------- | ----------------------------------- |
| Custom Branding          | Skill & Task Management                             | Employee Onboarding & Offboarding | Digital Schedule Viewing            |
| Time Clock Configuration | Schedule Template & Duplication                     |                                   | View Team Shifts                    |
| Accounting Integration   | Automatic Schedule Generation & Optimization        |                                   | Request Time Off                    |
| User Role Management     | Manual Schedule Generation with Conflict Prevention |                                   | Call in Sick                        |
| Global Toggle Features   | Employee Availability and Recurring Shifts          |                                   | Update Availabilty                  |
|                          | Sick & Vacation Time Review & Notifications         |                                   | Shift Swap Requests & Notifications |
|                          | Attendance Pattern Insights                         |                                   |                                     |
|                          | Shift Swap Approval & Notifications                 |                                   |                                     |
|                          | Data Exports & Printable Schedules                  |                                   |                                     |
|                          | Configure Hours Restrictions by Employee            |                                   |                                     |
|                          | Overtime Minimization Tools                         |                                   |                                     |


## Tech Stack

- **Backend:** FastAPI
- **Frontend:** React
- **Database:** MongoDB
- **Scheduling Engine:** Google OR-Tools
- **Containerization:** Docker


## Demo

<!-- Add a screenshot, GIF, or link to a live demo -->
TODO
<!-- ![Screenshot](docs/screenshot.png) -->


## Installation

### Prerequisites

- [Docker](https://www.docker.com/)
<!-- - [UV](https://docs.astral.sh/uv/) 
- [Node.js](https://nodejs.org/en) -->

### Steps

```bash
# Clone the repository
git clone https://github.com/isaac987/punchedn.git
cd punchedn

# Copy environment file and configure
cp .env.example .env

# Build and start all services
docker compose -f compose.yml up --watch
```

The API Docs will be available at `http://api.localhost/docs` and the frontend at `http://localhost/`.


## Configuration

Environment variables (`.env`):

| Variable         | Type   | Default                        | Description                          |
|------------------|--------|----------------------------------|---------------------------------------|
| `APP_ENV`        | string | `development`                   | Application environment (`development`, `production`, etc.) |
| `MONGO_USER`     | string | `null`                          | MongoDB username                      |
| `MONGO_PASSWORD` | string | `null`                          | MongoDB password                      |
| `MONGO_HOST`     | string | `null`                          | MongoDB cluster host (e.g. `cluster.1234.mongodb.net`) |
| `MONGO_NAME`     | string | `null`                          | Database/application name             |
| `CADDY_DOMAIN`   | string | `localhost`                     | Domain used by Caddy for reverse proxy/TLS |

## Roadmap
TODO
<!-- - [x] Core scheduling engine (OR-Tools integration)
- [x] Role-based permissions system
- [ ] Shift swap workflow
- [ ] Accounting integrations (QuickBooks, Xero, FreshBooks, Wave)
- [ ] Mobile app
- [ ] Physical time clock / NFC support

See the [open issues](https://github.com/username/punchedn/issues) for the full list of proposed features and known issues. -->


## Contributing

Contributions are welcome!

1. Fork the project
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct and pull request process.


## Testing
TODO
<!-- ```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test
``` -->

## License

Distributed under the MIT License. See [`LICENSE`](LICENSE) for more information.

## Acknowledgments
TODO
<!-- - [Google OR-Tools](https://developers.google.com/optimization) for schedule optimization
- [FastAPI](https://fastapi.tiangolo.com/)
- [React](https://react.dev/) -->

---
