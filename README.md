# Tech Stack Docker Playground / 技术栈 Docker 游乐场

[English](#english) | [中文](#中文)

---

<a name="english"></a>
## 🇬🇧 English

Welcome to the **Tech Stack Docker Playground**! 🚀

This project is designed to help developers learn, demonstrate, experiment, and test features of various common technology stacks using Docker. By providing ready-to-use Docker Compose environments, it lowers the barrier to entry for exploring new tools and understanding their core concepts.

### 🎯 Project Goals

- **Learn by Doing**: Provide hands-on environments to learn new technologies.
- **Demonstrate Features**: Showcase specific features of different tech stacks (e.g., Master-Slave replication in MySQL).
- **Experimentation**: A safe sandbox to run experiments, test configurations, and benchmark performance.
- **Easy Setup**: Use Docker and Docker Compose to ensure consistent and reproducible environments across different machines.

### 📂 Project Structure

The repository is organized by technology stack. Each directory contains a self-contained environment for a specific tool.

#### Current Stacks

- **[MySQL](./mysql/)**: A complete MySQL 8.0 Master-Slave replication setup with a rich business database schema, batch data insertion capabilities, and performance testing scripts.

#### Upcoming Stacks

- **Redis**: (Coming Soon) Environments for exploring Redis caching, persistence, clustering, and more.

### 🚀 Getting Started

To get started with a specific technology, navigate to its directory and follow the instructions in its respective `README.md`.

For example, to explore the MySQL environment:

```bash
cd mysql
# Follow the instructions in mysql/README.md
make start
```

### 🛠 Prerequisites

To use the environments in this repository, you will need:

- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/install/)
- `make` utility (optional but highly recommended for running predefined commands)

### 🤝 Contributing

Contributions are welcome! If you have an idea for a new tech stack environment, a new experiment, or improvements to existing ones, feel free to open an issue or submit a pull request.

### 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

<a name="中文"></a>
## 🇨🇳 中文

欢迎来到 **技术栈 Docker 游乐场 (Tech Stack Docker Playground)**！🚀

本项目旨在帮助开发者使用 Docker 学习、演示、实验和测试各种常见技术栈的功能。通过提供开箱即用的 Docker Compose 环境，降低了探索新工具和理解其核心概念的门槛。

### 🎯 项目目标

- **在实践中学习**：提供动手实践的环境来学习新技术。
- **功能演示**：展示不同技术栈的特定功能（例如，MySQL 中的主从复制）。
- **实验沙箱**：提供一个安全的沙箱来运行实验、测试配置和进行性能基准测试。
- **轻松搭建**：使用 Docker 和 Docker Compose 确保在不同机器上拥有一致且可重复的环境。

### 📂 项目结构

代码库按技术栈组织。每个目录都包含特定工具的独立环境。

#### 当前支持的技术栈

- **[MySQL](./mysql/)**：一个完整的 MySQL 8.0 主从复制环境，包含丰富的业务数据库模式、批量数据插入功能和性能测试脚本。

#### 即将推出的技术栈

- **Redis**：（即将推出）用于探索 Redis 缓存、持久化、集群等功能的环境。

### 🚀 快速开始

要开始使用特定的技术栈，请导航到其目录并按照其各自的 `README.md` 中的说明进行操作。

例如，要探索 MySQL 环境：

```bash
cd mysql
# 按照 mysql/README.md 中的说明进行操作
make start
```

### 🛠 前置条件

要使用此代码库中的环境，您需要：

- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/install/)
- `make` 工具（可选，但强烈建议用于运行预定义的命令）

### 🤝 参与贡献

欢迎贡献！如果您对新的技术栈环境、新的实验或对现有环境的改进有任何想法，请随时提交 Issue 或 Pull Request。

### 📄 许可证

本项目采用 MIT 许可证 - 详情请参阅 [LICENSE](LICENSE) 文件。
