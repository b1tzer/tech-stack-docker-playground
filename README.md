# Tech Stack Docker Playground

Welcome to the **Tech Stack Docker Playground**! 🚀

This project is designed to help developers learn, demonstrate, experiment, and test features of various common technology stacks using Docker. By providing ready-to-use Docker Compose environments, it lowers the barrier to entry for exploring new tools and understanding their core concepts.

## 🎯 Project Goals

- **Learn by Doing**: Provide hands-on environments to learn new technologies.
- **Demonstrate Features**: Showcase specific features of different tech stacks (e.g., Master-Slave replication in MySQL).
- **Experimentation**: A safe sandbox to run experiments, test configurations, and benchmark performance.
- **Easy Setup**: Use Docker and Docker Compose to ensure consistent and reproducible environments across different machines.

## 📂 Project Structure

The repository is organized by technology stack. Each directory contains a self-contained environment for a specific tool.

### Current Stacks

- **[MySQL](./mysql/)**: A complete MySQL 8.0 Master-Slave replication setup with a rich business database schema, batch data insertion capabilities, and performance testing scripts.

### Upcoming Stacks

- **Redis**: (Coming Soon) Environments for exploring Redis caching, persistence, clustering, and more.

## 🚀 Getting Started

To get started with a specific technology, navigate to its directory and follow the instructions in its respective `README.md`.

For example, to explore the MySQL environment:

```bash
cd mysql
# Follow the instructions in mysql/README.md
make start
```

## 🛠 Prerequisites

To use the environments in this repository, you will need:

- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/install/)
- `make` utility (optional but highly recommended for running predefined commands)

## 🤝 Contributing

Contributions are welcome! If you have an idea for a new tech stack environment, a new experiment, or improvements to existing ones, feel free to open an issue or submit a pull request.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
