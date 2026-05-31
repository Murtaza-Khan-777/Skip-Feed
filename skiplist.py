import random

class Node:
  def __init__(self, data, level):
    self.data = data
    self.forward = [None] * (level + 1)


class SkipList:
  def __init__(self, maxlevel):
    self.maxlevel = maxlevel
    self.header = Node(-1, self.maxlevel)
    self.current_level = 0

  def get_random_level(self):
    level = 0
    while random.random() < 0.5 and level < self.maxlevel -1:
      level += 1
    return level
  
  def insert(self,data):
    update = [None] * (self.maxlevel + 1)
    current = self.header

    for i in range(self.current_level, -1, -1):
      while current.forward[i] and current.forward[i].data < data:
        current = current.forward[i]
      update[i] = current

    new_level = self.get_random_level()

    if new_level > self.current_level:
      for i in range(self.current_level + 1, new_level + 1):
        update[i] = self.header
      self.current_level = new_level
    
    new_node = Node(data, new_level)
    for i in range(new_level + 1):
      new_node.forward[i] = update[i].forward[i]
      update[i].forward[i] = new_node

  def search(self, data , index,output):
    current = self.header
    for i in range(self.current_level, -1, -1):
      while current.forward[i] and current.forward[i].data[index] < data:
        current = current.forward[i]
    
    current = current.forward[0]
    
    if current and current.data[index] == data:
      return current.data[output]
    return []
  
  def to_list(self):
      nodes = []
      current = self.header.forward[0] 
      
      while current is not None:
          nodes.append(current.data)
          current = current.forward[0]
          
      return nodes
  
class PostSkipList(SkipList): # A specialized skiplist for posts, storing specific data at each level
    def insert_at_level(self, data, level):
      update = [None] * (self.maxlevel + 1)
      current = self.header   # start from the header node

      for i in range(self.current_level, -1, -1):
          while current.forward[i] and current.forward[i].data[0] < data[0]:
              current = current.forward[i]
          update[i] = current

      new_level = min(level, self.maxlevel)  # ensure the new level does not exceed max level and is determined by the parameter level

      if new_level > self.current_level: # if the new level is greater than current level, initialize references for the new level to the header
          for i in range(self.current_level + 1, new_level + 1): 
              update[i] = self.header
          self.current_level = new_level

      new_node = Node(data, new_level) # create a new node with the post data and the determined level which is the level parameter passed in the function
      for i in range(new_level + 1):
          new_node.forward[i] = update[i].forward[i]
          update[i].forward[i] = new_node

    def traverse_level(self, level): # traverses a specific level and retruns a list of post data at that level
        results = []
        current = self.header.forward[level] 
        while current is not None:
            results.append(current.data) #goes forward until none is found and appends the data at that level to the results list
            current = current.forward[level]
        return results