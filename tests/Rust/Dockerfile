FROM rust:1.84.0-alpine
WORKDIR /usr/src/app
COPY . /usr/src/app
RUN cargo new code && mv sample_code.rs code/src/main.rs
CMD ["sleep", "infinity"]