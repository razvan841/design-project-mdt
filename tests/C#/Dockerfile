# Use the .NET SDK image
FROM mcr.microsoft.com/dotnet/sdk:8.0 AS build


WORKDIR /app
COPY . .

RUN dotnet new console -n MyApp
RUN mv *.cs MyApp/
RUN rm MyApp/Program.cs

WORKDIR /app/MyApp
CMD ["sleep", "infinity"]
