define my_macro
	bash -c 'i=5; echo "$$$$i"'
endef

test:
	$(call my_macro)
