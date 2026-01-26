# Blender addon installation
# Usage: make install-addon [BLENDER_VERSION=3.6]
BLENDER_VERSION ?= 4.3
ADDON_NAME = libsm64-blender
BLENDER_ADDONS_DIR = $(HOME)/Library/Application Support/Blender/$(BLENDER_VERSION)/scripts/addons/$(ADDON_NAME)
BLENDER_ALL_ADDONS_DIR = $(HOME)/Library/Application Support/Blender/$(BLENDER_VERSION)/scripts/addons

install-addon:
		@echo "Installing addon to $(BLENDER_ADDONS_DIR)..."
		@mkdir -p "$(BLENDER_ADDONS_DIR)"
		@rsync -av --exclude='.git' --exclude='.gitignore' --exclude='Makefile' ./ "$(BLENDER_ADDONS_DIR)/"
		@echo "Addon installed successfully!"

list-addons:
		@echo "Listing Blender $(BLENDER_VERSION) addons:"
		@if [ -d "$(BLENDER_ALL_ADDONS_DIR)" ]; then \
				ls -la "$(BLENDER_ALL_ADDONS_DIR)"; \
		else \
				echo "No addons directory found at $(BLENDER_ALL_ADDONS_DIR)"; \
		fi

.PHONY: install-addon list-addons
