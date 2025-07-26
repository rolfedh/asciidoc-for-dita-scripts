#!/usr/bin/env bash
# Bash completion script for adt (AsciiDoc DITA Toolkit)
#
# Installation:
#   # System-wide (requires sudo):
#   sudo cp scripts/adt-completion.bash /etc/bash_completion.d/adt
#   
#   # User-specific:
#   mkdir -p ~/.local/share/bash-completion/completions
#   cp scripts/adt-completion.bash ~/.local/share/bash-completion/completions/adt
#   
#   # Or source directly in ~/.bashrc:
#   source /path/to/asciidoc-dita-toolkit/scripts/adt-completion.bash

_adt_completion() {
    local cur prev words cword
    _init_completion || return

    # Current word being completed
    cur="${COMP_WORDS[COMP_CWORD]}"
    prev="${COMP_WORDS[COMP_CWORD-1]}"

    # Base adt options
    local base_opts="--help --version --list-modules --suppress-warnings --show-warnings"
    
    # Get available modules dynamically from completion helper
    local modules=""
    if command -v python3 >/dev/null 2>&1; then
        modules=$(python3 -m asciidoc_dita_toolkit.adt_core.completion modules 2>/dev/null)
    fi
    
    # If dynamic discovery fails, use fallback list
    if [[ -z "$modules" ]]; then
        modules="ArchiveUnusedFiles ContentType ContextAnalyzer ContextMigrator CrossReference DirectoryConfig EntityReference ExampleBlock UserJourney ValeFlagger"
    fi
    
    # UserJourney subcommands
    local journey_commands="start resume continue status list cleanup"
    
    # Module-specific options
    local module_opts="-f --file -r --recursive -d --directory -v --verbose -h --help"
    
    # ValeFlagger-specific options
    local valeflag_opts="--enable-rules --disable-rules --config --execute-changes"
    
    # UserJourney-specific options  
    local journey_opts="-n --name --completed --all"

    case "${COMP_CWORD}" in
        1)
            # First argument: complete with modules and base options
            COMPREPLY=($(compgen -W "${modules} ${base_opts}" -- "${cur}"))
            ;;
        2)
            # Second argument depends on first
            case "${prev}" in
                journey)
                    # UserJourney subcommands
                    COMPREPLY=($(compgen -W "${journey_commands}" -- "${cur}"))
                    ;;
                ValeFlagger)
                    # ValeFlagger options
                    COMPREPLY=($(compgen -W "${module_opts} ${valeflag_opts}" -- "${cur}"))
                    ;;
                UserJourney|ContentType|EntityReference|DirectoryConfig|ContextAnalyzer|ContextMigrator|CrossReference|ExampleBlock|ArchiveUnusedFiles)
                    # Standard module options
                    COMPREPLY=($(compgen -W "${module_opts}" -- "${cur}"))
                    ;;
                *)
                    # No completion for other base options
                    COMPREPLY=()
                    ;;
            esac
            ;;
        3)
            # Third argument
            case "${COMP_WORDS[1]}" in
                journey)
                    case "${prev}" in
                        start|resume|continue|status|cleanup)
                            # Journey command options
                            COMPREPLY=($(compgen -W "${journey_opts}" -- "${cur}"))
                            ;;
                    esac
                    ;;
                *)
                    # Handle option values
                    case "${prev}" in
                        -f|--file)
                            # Complete with .adoc files
                            COMPREPLY=($(compgen -f -X '!*.adoc' -- "${cur}"))
                            ;;
                        -d|--directory)
                            # Complete with directories
                            COMPREPLY=($(compgen -d -- "${cur}"))
                            ;;
                        -c|--config)
                            # Complete with config files (.yaml, .yml, .json)
                            COMPREPLY=($(compgen -f -X '!*.@(yaml|yml|json)' -- "${cur}"))
                            ;;
                        -n|--name)
                            # Complete with existing journey names if available
                            local journeys=""
                            if command -v adt >/dev/null 2>&1; then
                                journeys=$(adt journey list 2>/dev/null | grep -E '^\s*[a-zA-Z]' | awk '{print $1}' | tr '\n' ' ')
                            fi
                            COMPREPLY=($(compgen -W "${journeys}" -- "${cur}"))
                            ;;
                        --enable-rules|--disable-rules)
                            # Common Vale rules (could be enhanced to read from config)
                            local vale_rules="Headings.Capitalization Terms.Use Style.Passive Microsoft.Contractions"
                            COMPREPLY=($(compgen -W "${vale_rules}" -- "${cur}"))
                            ;;
                        *)
                            # Default file completion for other cases
                            COMPREPLY=($(compgen -f -- "${cur}"))
                            ;;
                    esac
                    ;;
            esac
            ;;
        *)
            # For arguments beyond 3, provide contextual completion
            case "${prev}" in
                -f|--file)
                    COMPREPLY=($(compgen -f -X '!*.adoc' -- "${cur}"))
                    ;;
                -d|--directory)
                    COMPREPLY=($(compgen -d -- "${cur}"))
                    ;;
                -c|--config)
                    COMPREPLY=($(compgen -f -X '!*.@(yaml|yml|json)' -- "${cur}"))
                    ;;
                *)
                    # No completion for other cases
                    COMPREPLY=()
                    ;;
            esac
            ;;
    esac

    return 0
}

# Register completion for adt command
complete -F _adt_completion adt