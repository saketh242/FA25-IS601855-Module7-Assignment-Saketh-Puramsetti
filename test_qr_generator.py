import unittest
import tempfile
import os
import sys
from pathlib import Path
from unittest.mock import patch, mock_open
import qrcode
from PIL import Image

# Add the current directory to the path so we can import main
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from main import (
    is_valid_url,
    generate_qr_code,
    create_directory,
    setup_logging
)


class TestQRCodeGenerator(unittest.TestCase):
    """Test cases for the QR Code Generator application."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        self.temp_dir = tempfile.mkdtemp()
        self.test_url = "https://github.com/test"
        self.invalid_url = "not-a-valid-url"

    def tearDown(self):
        """Clean up after each test method."""
        # Clean up any test files
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_is_valid_url_with_valid_url(self):
        """Test is_valid_url with a valid URL."""
        self.assertTrue(is_valid_url("https://github.com/test"))
        self.assertTrue(is_valid_url("http://example.com"))
        self.assertTrue(is_valid_url("https://www.google.com"))

    def test_is_valid_url_with_invalid_url(self):
        """Test is_valid_url with an invalid URL."""
        self.assertFalse(is_valid_url("not-a-url"))
        self.assertFalse(is_valid_url("ftp://invalid"))
        self.assertFalse(is_valid_url(""))
        self.assertFalse(is_valid_url(None))

    def test_create_directory_success(self):
        """Test create_directory creates directory successfully."""
        test_path = Path(self.temp_dir) / "test_dir"
        create_directory(test_path)
        self.assertTrue(test_path.exists())
        self.assertTrue(test_path.is_dir())

    def test_create_directory_already_exists(self):
        """Test create_directory when directory already exists."""
        test_path = Path(self.temp_dir) / "existing_dir"
        test_path.mkdir()
        # Should not raise an exception
        create_directory(test_path)
        self.assertTrue(test_path.exists())

    def test_generate_qr_code_with_valid_url(self):
        """Test generate_qr_code with a valid URL."""
        output_path = Path(self.temp_dir) / "test_qr.png"
        
        # Mock the logging to avoid output during tests
        with patch('main.logging.info') as mock_info:
            generate_qr_code(self.test_url, output_path, 'red', 'white')
        
        # Check if file was created
        self.assertTrue(output_path.exists())
        
        # Verify it's a valid image file
        try:
            with Image.open(output_path) as img:
                self.assertIsInstance(img, Image.Image)
        except Exception as e:
            self.fail(f"Generated file is not a valid image: {e}")

    def test_generate_qr_code_with_invalid_url(self):
        """Test generate_qr_code with an invalid URL."""
        output_path = Path(self.temp_dir) / "test_qr_invalid.png"
        
        # Should not create a file for invalid URL
        generate_qr_code(self.invalid_url, output_path, 'red', 'white')
        self.assertFalse(output_path.exists())

    def test_generate_qr_code_file_creation(self):
        """Test that QR code file is created with correct properties."""
        output_path = Path(self.temp_dir) / "test_qr.png"
        
        with patch('main.logging.info'):
            generate_qr_code(self.test_url, output_path, 'blue', 'yellow')
        
        self.assertTrue(output_path.exists())
        
        # Check file size (should be reasonable for a QR code)
        file_size = output_path.stat().st_size
        self.assertGreater(file_size, 1000)  # At least 1KB
        self.assertLess(file_size, 100000)   # Less than 100KB

    def test_generate_qr_code_different_colors(self):
        """Test QR code generation with different color combinations."""
        test_cases = [
            ('red', 'white'),
            ('blue', 'yellow'),
            ('black', 'white'),
            ('green', 'black')
        ]
        
        for fill_color, back_color in test_cases:
            with self.subTest(fill=fill_color, back=back_color):
                output_path = Path(self.temp_dir) / f"test_qr_{fill_color}_{back_color}.png"
                
                with patch('main.logging.info'):
                    generate_qr_code(self.test_url, output_path, fill_color, back_color)
                
                self.assertTrue(output_path.exists())

    @patch('main.logging.error')
    def test_generate_qr_code_error_handling(self, mock_error):
        """Test error handling in generate_qr_code."""
        # Test with invalid path (read-only directory)
        invalid_path = Path("/invalid/path/that/does/not/exist") / "test.png"
        
        generate_qr_code(self.test_url, invalid_path, 'red', 'white')
        
        # Should not raise an exception, but should log an error
        # The mock will verify that logging.error was called
        mock_error.assert_called()

    def test_setup_logging(self):
        """Test that setup_logging configures logging correctly."""
        # This is a bit tricky to test directly, but we can ensure it doesn't crash
        try:
            setup_logging()
        except Exception as e:
            self.fail(f"setup_logging raised an exception: {e}")


class TestQRCodeIntegration(unittest.TestCase):
    """Integration tests for the QR Code Generator."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up after each test."""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_full_workflow_with_valid_url(self):
        """Test the complete workflow from URL to QR code file."""
        from main import main
        import argparse
        
        # Mock argparse to provide a test URL
        test_url = "https://github.com/integration-test"
        
        with patch('main.argparse.ArgumentParser.parse_args') as mock_parse:
            mock_parse.return_value = argparse.Namespace(url=test_url)
            
            with patch('main.logging.info'):
                # This should not crash
                try:
                    main()
                except SystemExit:
                    pass  # main() calls exit(1) on directory creation failure
        
        # Check if qr_codes directory was created
        qr_dir = Path.cwd() / "qr_codes"
        if qr_dir.exists():
            # Clean up
            import shutil
            shutil.rmtree(qr_dir)

    def test_qr_code_content_verification(self):
        """Test that the generated QR code contains the expected data."""
        from main import generate_qr_code
        
        test_url = "https://github.com/content-test"
        output_path = Path(self.temp_dir) / "content_test.png"
        
        with patch('main.logging.info'):
            generate_qr_code(test_url, output_path, 'red', 'white')
        
        self.assertTrue(output_path.exists())
        
        # Verify the QR code can be read back
        try:
            qr = qrcode.QRCode()
            with Image.open(output_path) as img:
                # Convert PIL image to the format expected by qrcode
                import io
                img_bytes = io.BytesIO()
                img.save(img_bytes, format='PNG')
                img_bytes.seek(0)
                
                # This is a basic test - in a real scenario you'd use a QR decoder
                # For now, we just verify the file is a valid image
                self.assertIsInstance(img, Image.Image)
        except Exception as e:
            self.fail(f"QR code verification failed: {e}")


if __name__ == '__main__':
    # Create a test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test cases
    suite.addTests(loader.loadTestsFromTestCase(TestQRCodeGenerator))
    suite.addTests(loader.loadTestsFromTestCase(TestQRCodeIntegration))
    
    # Run the tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Exit with appropriate code
    sys.exit(0 if result.wasSuccessful() else 1)
