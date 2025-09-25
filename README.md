# NotionAutomator

This project is my attempt at automating work in Notion. There may be some bugs, but if it's helpful to you, please give me a star. ⭐️

> If you meet any problems during use or would like to suggest new features to enhance this project, please feel free to create an issue. 😁

## Table of contents

<!--toc:start-->
- [NotionAutomator](#notionautomator)
  - [Table of contents](#table-of-contents)
  - [Setup](#setup)
  - [Configuration](#configuration)
  - [Usage](#usage)
  - [Acknowledgment](#acknowledgment)
  - [FAQ](#faq)
<!--toc:end-->

## Setup

- Install the dependencies with the following command.

    ```sh
    pip install -r requirements.txt
    ```

- For development, you can install the dependencies with the following command.

    ```sh
    pip install -r requirements-dev.txt
    ```

## Configuration

The default configuration file is [configs/default.yaml](./configs/default.yaml). You can modify it according to your needs.

## Usage

Run the following command to start the program.

```sh
python main.py -c configs/default.yaml # change to the path to your config file
```

## Acknowledgment

💗 Thanks for these great works:

- [arxiv](https://github.com/lukasschwab/arxiv.py)
- [notion-py](https://github.com/jamalex/notion-py)
- [notion-sdk-py](https://github.com/ramnes/notion-sdk-py)

## FAQ

> Q1: Error - arxiv.arxiv.HTTPError: Page request resulted in HTTP 502
> A1: A non-200 status encountered while fetching a page of results from arXiv, retry or clean your cookies.
> Q2: Error - httpx.ConnectError: EOF occurred in violation of protocol
> A2: This error is caused by the proxy, check out your proxy and retry.
