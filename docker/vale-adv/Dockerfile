FROM jdkato/vale:latest

# Create a temporary vale configuration to install the AsciiDocDITA package
RUN echo "StylesPath = /root/.local/share/vale/styles" > /tmp/.vale.ini && \
    echo "Packages = https://github.com/jhradilek/asciidoctor-dita-vale/releases/latest/download/AsciiDocDITA.zip" >> /tmp/.vale.ini && \
    vale --config=/tmp/.vale.ini sync && \
    rm /tmp/.vale.ini

# Set working directory
WORKDIR /docs

# Use Vale directly as entrypoint
ENTRYPOINT ["vale"]