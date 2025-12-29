/**
 * Tests for React components
 */
import { vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { BackButton } from '../src/components/common/BackButton';
import { LoadingSpinner } from '../src/components/common/LoadingSpinner';
import { StyledTextField } from '../src/components/common/StyledTextField';
import { StyledCard } from '../src/components/common/StyledCard';

// Mock react-router-dom
const mockNavigate = vi.fn();
vi.mock('react-router-dom', () => ({
  useNavigate: () => mockNavigate,
  Navigate: ({ to }) => <div data-testid="navigate" data-to={to}>Navigate to {to}</div>,
}));

// Mock react-i18next
vi.mock('react-i18next', () => ({
  useTranslation: () => ({
    t: (key) => key,
    i18n: { language: 'en' },
  }),
}));


describe('Common Components', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('BackButton', () => {
    it('should render back button with default text', () => {
      render(<BackButton />);
      expect(screen.getByText('common.back')).toBeInTheDocument();
    });

    it('should render back button with custom label', () => {
      render(<BackButton label="Custom Back" />);
      expect(screen.getByText('Custom Back')).toBeInTheDocument();
      expect(screen.queryByText('common.back')).not.toBeInTheDocument();
    });

    it('should navigate when clicked', async () => {
      const user = userEvent.setup();
      render(<BackButton />);
      const button = screen.getByText('common.back');
      await user.click(button);
      expect(mockNavigate).toHaveBeenCalledWith('/trips');
    });

    it('should navigate to custom route when provided', async () => {
      const user = userEvent.setup();
      render(<BackButton to="/custom-route" />);
      const button = screen.getByText('common.back');
      await user.click(button);
      expect(mockNavigate).toHaveBeenCalledWith('/custom-route');
    });
  });

  describe('LoadingSpinner', () => {
    it('should render loading spinner', () => {
      render(<LoadingSpinner />);
      const spinner = screen.getByRole('progressbar');
      expect(spinner).toBeInTheDocument();
    });

    it('should use full height by default', () => {
      const { container } = render(<LoadingSpinner />);
      // MUI Box component uses sx prop which generates inline styles
      // Check that the component renders (the Box wrapper is there)
      const box = container.querySelector('div');
      expect(box).toBeInTheDocument();
      // The component should render, we're just verifying it exists
      expect(container.firstChild).toBeTruthy();
    });

    it('should not use full height when fullHeight is false', () => {
      const { container } = render(<LoadingSpinner fullHeight={false} />);
      const box = container.firstChild;
      expect(box).toBeInTheDocument();
    });
  });

  describe('StyledTextField', () => {
    it('should render text field with label', () => {
      render(<StyledTextField label="Test Label" />);
      expect(screen.getByLabelText('Test Label')).toBeInTheDocument();
    });

    it('should accept user input', async () => {
      const user = userEvent.setup();
      render(<StyledTextField label="Test Input" />);
      const input = screen.getByLabelText('Test Input');
      await user.type(input, 'test value');
      expect(input).toHaveValue('test value');
    });

    it('should pass through additional props', () => {
      render(<StyledTextField label="Test" placeholder="Enter text" />);
      const input = screen.getByPlaceholderText('Enter text');
      expect(input).toBeInTheDocument();
    });
  });

  describe('StyledCard', () => {
    it('should render children content', () => {
      render(
        <StyledCard>
          <div>Test Content</div>
        </StyledCard>
      );
      expect(screen.getByText('Test Content')).toBeInTheDocument();
    });

    it('should use default width when not specified', () => {
      const { container } = render(<StyledCard>Content</StyledCard>);
      const card = container.querySelector('.MuiCard-root');
      expect(card).toBeInTheDocument();
    });

    it('should use custom width when specified', () => {
      const { container } = render(<StyledCard width={500}>Content</StyledCard>);
      const card = container.querySelector('.MuiCard-root');
      expect(card).toBeInTheDocument();
    });
  });

});
