class Tree:
    """Abstract base class representing a tree structure."""

    #------------------------------- nested Position class -------------------------------
    class Position:
        """An abstraction representing the location of a single element."""

        def element(self):
            """Return the element stored at this Position."""
            raise NotImplementedError('must be implemented by subclass')

        def __eq__(self, other):
            """Return True if other Position represents the same location."""
            raise NotImplementedError('must be implemented by subclass')

        def __ne__(self, other):
            """Return True if other does not represent the same location."""
            return not (self == other) # opposite of eq

    # ---------- abstract methods that concrete subclass must support ----------
    def root(self):
        """Return Position representing the tree s root (or None if empty)."""
        raise NotImplementedError('must be implemented by subclass')

    def parent(self, p):
        """Return Position representing p s parent (or None if p is root)."""
        raise NotImplementedError('must be implemented by subclass')

    def num_children(self, p):
        """Return the number of children that Position p has."""
        raise NotImplementedError('must be implemented by subclass')

    def children(self, p):
        """Generate an iteration of Positions representing p s children."""
        raise NotImplementedError('must be implemented by subclass')

    def __len__(self):
        """Return the total number of elements in the tree."""
        raise NotImplementedError('must be implemented by subclass')
    # ---------- concrete methods implemented in this class ----------
    def is_root(self, p):
        """Return True if Position p represents the root of the tree."""
        return self.root( ) == p

    def is_leaf(self, p):
        """Return True if Position p does not have any children."""
        return self.num_children(p) == 0

    def is_empty(self):
        """Return True if the tree is empty."""
        return len(self) == 0
    
    def depth(self, p):
        """Return the number of levels separating Position p from the root."""
        if self.is_root(p):
            return 0
        else:
            return 1 + self.depth(self.parent(p))

    def _height2(self, p): # time is linear in size of subtree
        """Return the height of the subtree rooted at Position p."""
        if self.is_leaf(p):
            return 0
        else:
            return 1 + max(self._height2(c) for c in self.children(p))

    def height(self, p=None):
        """ Return the height of the subtree rooted at Position p.
            If p is None, return the height of the entire tree.
        """
        if p is None:
            p = self.root()
        return self._height2(p) # start height2 recursion
        
class LinkedTree(Tree):

    class _Node: # A private class for storing nodes
        __slots__ = '_element', '_parent', '_children'
        
        def __init__(self, element, parent=None, children=None):
            self._element = element
            self._parent = parent
            self._children = children
            
    class Position(Tree.Position):
        
        def __init__(self, container, node):
            """Constructor should not be invoked by user."""
            self._container = container
            self._node = node

        def element(self):
            """Return the element stored at this Position."""
            return self._node._element

        def __eq__(self, other):
            """Return True if other is a Position representing the same location."""
            return type(other) is type(self) and other._node is self._node
        
    def _validate(self, p):
        """Return associated node, if position is valid."""
        if not isinstance(p, self.Position):
            raise TypeError('p must be proper Position type')
        if p._container is not self:
            raise ValueError('p does not belong to this container')
        if p._node._parent is p._node: # convention for deprecated nodes
            raise ValueError('p is no longer valid')
        return p._node


    def _make_position(self, node):
        """Return Position instance for given node (or None if no node)."""
        return self.Position(self, node) if node is not None else None
        
    def __init__(self):
        self._root = None
        self._size = 0
        
    def __len__(self):
        return self._size
        
    def root(self):
        return self._make_position(self._root)
        
    def parent(self, p):
        node = self._validate(p)
        return self._make_position(node._parent)
        
    def num_children(self, p):
        node = self._validate(p)
        if node._children is None:
            return 0
        else:
            return len(node._children)
        
    def children(self, p):
        node = self._validate(p)
        if node is not None and node._children is not None:
            for child in node._children:
                yield self._make_position(child)
        
    def _add_root(self, e):
        if self._root is not None: raise ValueError('Root exists')
        self._size = 1
        self._root = self._Node(e)
        return self._make_position(self._root)
        
    def _add_nonroot_node(self, p, e):
        node = self._validate(p)
        if node is None: raise ValueError('No such position exists')
        if node._children is None:
            node._children = []

        if self.find_child_by_value(p, e):
            return
        else:
            self._size = self.__len__() + 1
            newNode = self._Node(e, node)
            node._children.append(newNode)
        # TODO: Need to make sure that there is no child with the same value.
        # TODO Do not forget to update the _size.
        # TODO: Create a new node with the value.
        # TODO. Add it to the children list of node p.
        return self._make_position(newNode)
        
    def add_node(self, e, p=None):
        """Add new node to tree. Provide no position to add as root."""
        if p is None:
            self._add_root(e)
        else:
            self._add_nonroot_node(p, e)
        
    def _traverse_preorder(self, p):
        """Returns a generator that yields nodes in pre-order"""
        yield self.depth(p)*'\t' + self._validate(p)._element + '\n'
        for child in self.children(p):
            yield from self._traverse_preorder(child)


    def _traverse_postorder(self, p):
        """Returns a generator that yields nodes in post-order"""
        for child in self.children(p):
            yield from self._traverse_postorder(child)
        yield self.depth(p)*'\t' + self._validate(p)._element + '\n'


    def all_nodes(self, mode):
        g = None
        if mode == 'pre':
            g = self._traverse_preorder(self.root())
        else:
            g = self._traverse_postorder(self.root())
        for n in g:
            yield n
        
    def get_path_to_root(self, p):
        """returns an ordered list of positions from p to root (including p and root) """
        orderedList = []
        orderedList.append(p)

        while(self.is_root(p) is False):
            p = self.parent(p)
            orderedList.append(p)

        return orderedList

    def find_child_by_value(self, p, value):
        """Returns the position of the child of p with value """
        for child in self.children(p):
            if self._validate(child)._element == value:
                return child
        return False
        
class ProductCategorizer:
    
    def __init__(self, data_file_path):
        self._data_file_path = data_file_path
        self._tree = None
        
    def fill_tree(self):
        """Read the categoric data from input file line by line and blow up the tree"""
        self._tree = LinkedTree()
        parent = None
        with open(self._data_file_path) as file:
            for line in file.readlines():
                if self._tree.is_empty():
                    self._tree.add_node(line.strip())
                else:
                    nodes = line.split(',')
                    for node in nodes:
                        if self._tree._validate(self._tree.root())._element == node.strip():
                            parent = self._tree.root()
                            continue
                        else:
                            if self._tree.find_child_by_value(parent, node.strip()) is False:
                                self._tree.add_node(node.strip(), parent)
                            else:
                                parent = self._tree.find_child_by_value(self._tree.root(), node.strip())
        # TODO
        # For each line in the file,
        # Consider the line as a path from root to a leaf node
        # If such a path exists, skip to next line.
        # Otherwise, create the necessary nodes so that the path exists in the tree.
        
    def print_tree(self):
        """print the tree in preorder and postorder manner"""
        # TODO You should have two output files for post- and pre-order traversals.
        # The hierarchy should be explicit in the output files with tabs.
        with open('pre.txt', 'w') as pre:
            for node in self._tree.all_nodes('pre'):
                pre.write(node)
        with open('post.txt', 'w') as post:
            for node in self._tree.all_nodes('post'):
                post.write(node)
        