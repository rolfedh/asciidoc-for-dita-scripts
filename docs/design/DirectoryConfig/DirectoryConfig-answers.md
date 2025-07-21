## Software Architect Recommendations for ADT Directory Configuration MVP

### 1. **Configuration File Priority** ✅ RESOLVED
**Recommendation:** Display all configurations with most recent "last used" timestamp preselected. User confirms choice and can set a default to avoid future prompts.
- **Rationale:** Balances automation with user control, prevents silent configuration conflicts

### 2. **Plugin Integration** 
**Recommendation:** Modify the existing `process_adoc_files` function in `file_utils.py`
- **Rationale:** 
  - Single point of change ensures consistent behavior across all plugins
  - Maintains backward compatibility 
  - Follows DRY principle (Don't Repeat Yourself)
  - Minimal impact on existing plugin code

### 3. **Configuration Schema Location**
**Recommendation:** Core utility function that all plugins use (in `file_utils.py`)
- **Rationale:**
  - Configuration is infrastructure, not a plugin feature
  - Allows any plugin to benefit from directory scoping
  - Easier to maintain and test centrally
  - Follows separation of concerns principle

### 4. **Override Behavior**
**Recommendation:** Apply configuration filtering within the specified directory + warn user
- **Rationale:**
  - Honors user intent while maintaining safety
  - Clear feedback prevents confusion
  - Consistent with principle of least surprise

### 5. **Error Handling**
**Recommendation:** Warn and continue with other directories
- **Rationale:**
  - Graceful degradation keeps workflow moving
  - User gets feedback about issues without blocking progress
  - Aligns with Unix philosophy of "be liberal in what you accept"

### 6. **File Discovery Integration**
**Recommendation:** Modify existing `process_adoc_files` function
- **Rationale:**
  - Consistent with recommendation #2
  - Single source of truth for file discovery logic
  - Automatic benefit to all existing and future plugins

### 7. **CLI Structure**
**Recommendation:** New plugin following existing pattern
- **Rationale:**
  - Maintains architectural consistency
  - Leverages existing plugin infrastructure
  - Easy to discover via `adt --list-plugins`
  - Follows established patterns for easier maintenance

## Implementation Strategy
1. Add configuration utilities to `file_utils.py`
2. Modify `process_adoc_files` to be configuration-aware
3. Create `DirectoryConfig` plugin for configuration management
4. Update existing plugins automatically benefit from directory scoping

Let me know your preferences on these points and I'll implement the MVP accordingly!