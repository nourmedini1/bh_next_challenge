class TextProcessor:
    """
    A utility class to preprocess and chunk Markdown files.
    """
    def __init__(self):
        pass
    
    def split_markdown(self, markdown_text):
        """
        Splits markdown text into chunks based on headings (##, ###, etc.).

        Args:
            markdown_text (str): The raw markdown content.
        Returns:
            list: A list of text chunks, each corresponding to a section of the markdown.
        """
        sections = []
        current_section = []

        for line in markdown_text.splitlines():
            if line.startswith('#'):
                if current_section:
                    sections.append('\n'.join(current_section))
                    current_section = []
            current_section.append(line)

        if current_section:
            sections.append('\n'.join(current_section))

        return sections
    
         
    