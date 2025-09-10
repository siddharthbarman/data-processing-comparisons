from datetime import datetime
import sys
import csv          

PARENT_COUNT =4000
CHILDREN_PER_PARENT = 1000
CHILDREN_GENERATION_COUNT = 100

class SimpleTimer:
    def __init__(self):
        self.start()

    def start(self):
        self.start_time = datetime.now()

    def stop(self) -> int:
        self.stop_time = datetime.now()
        return (self.stop_time - self.start_time).total_seconds() * 1000 

class Parent:
    def __init__(self, name: str, children_per_parent: int):
        self.name = name
        self.children_per_parent = children_per_parent
        self.current_children_count = 0
        self.created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]

    def generate_children(self):
        if self.current_children_count == self.children_per_parent:
            return None
        else:
            result = []
            start = self.current_children_count
            for i in range(start, start + CHILDREN_GENERATION_COUNT, 1):
                childname = "{0}-child{1}".format(self.name, i)
                result.append(childname)
            self.current_children_count += len(result)
            return result
        

class Program:
    def __init__(self, output_file_path: str, parent_count: int, children_per_parent: int):
        self.parents: list[Parent] = []
        self.output_file_path = output_file_path
        self.parent_count = parent_count
        self.children_per_parent = children_per_parent
    
    def generate(self):
        outfile = open(self.output_file_path, "w", newline="")
        writer = csv.writer(outfile)
        header = ["ParentName", "ChildName", "EntryDate", "ExpectedChildrenCount", "ActionType"]
        writer.writerow(header)

        for i in range(0, self.parent_count, 1):
            parent_name = "Parent{0}".format(i)
            parent = Parent(parent_name, self.children_per_parent) 
            self.parents.append(parent)
        
        rows = []

        for i in range(0, self.parent_count, 1):
            parent = self.parents[i]
            row = [parent.name, "", datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3], self.children_per_parent, "FirstEntry"]
            rows.append(row)
                        
            children = parent.generate_children()
            if children != None:
                rows.extend(self.get_children_rows(parent, children))
            
            writer.writerows(rows)
            rows.clear()

        for times in range(0, 9, 1):        
            for i in range(0, self.parent_count, 1):
                parent = self.parents[i]
                children = parent.generate_children()
                if children != None:
                    rows.extend(self.get_children_rows(parent, children))            
                writer.writerows(rows)
                rows.clear()

        outfile.close()
    

    def get_children_rows(self, parent: Parent, children: list[str]):
        rows = []
        for child in children:
            row = [parent.name, child, datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3], "", "Child"]
            rows.append(row)
        return rows


def help():
    print("Generates raw parent and child records.")
    print("Usage:")
    print("  generate_raw <filepath.csv> <parent count> <children per parent>")


def main(argv: list[str]) -> int:
    if len(argv) != 4:
        help()
        return 0
    else:
        output_file_path = argv[1]
        if not argv[2].isdigit():
            print("Second argument must be an integer.")
            return 1
        if not argv[3].isdigit():
            print("Third argument must be an integer.")
            return 1
        parent_count = int(argv[2])
        children_per_parent = int(argv[3])
        program = Program(output_file_path, parent_count, children_per_parent)
        timer = SimpleTimer()
        program.generate()
        print("Total execution time:", timer.stop(), "ms.")


sys.exit(main(sys.argv))
