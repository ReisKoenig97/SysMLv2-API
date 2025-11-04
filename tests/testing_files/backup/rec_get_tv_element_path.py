def rec_get_tv_elementPath(self, path, tv, tv_item):
        """
        recursively build elementPath bottom up until root
        :param path: (incomplete path to tv_item, e.g. component1.TV_ITEM_TAG when the whole path is components.component1.TV_ITEM_TAG
        :param tv: TreeView Object
        :param tv_item: TreeView item to which the elementPath shall be generated
        :return: expanded incomplete elementpath(recursive step) or complete path to tv_item
        """
        if tv == None:
            self.logger.error("tv is None")
            return None
        if tv_item == None:
            self.logger.error("tv_item is None")
            return None
        tv_item_text = tv.item(tv_item, "text")
        tv_item_tag = self.get_tv_tag_value(tv_item_text)
        

        if tv_item.parent(tv_item) == None: return path
        """
        tv_tag = self.get_tv_tag_value(tv_item_text)
        if tv_tag=="<AUTOSAR>":
            return path
        """
        path_value = self.get_tv_AUTOSAR_path_value(tv_item_text)
        if path_value == None:
            while tv.parent(tv_item) != None and self.get_tv_AUTOSAR_path_value(tv.item(tv.parent(tv_item),"text")) == None:
                tv_item = tv.parent(tv_item)
            if tv.parent(tv_item) == None: path_value = self.get_tv_tag_value(tv.item(tv_item,"text"))
            else: path_value = self.get_tv_AUTOSAR_path_value(tv.item(tv.parent(tv_item),"text"))
            #path_value=tv_item_tag
        if path_value == None:
            self.logger.error(f"Path incomplete at {path}: tv_item has no path_value")
            return None

        return self.rec_get_tv_elementPath(f"{path_value}.{path}", tv, tv.parent(tv_item))