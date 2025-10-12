import React, { useState } from 'react';
import {
  AppBar,
  Toolbar,
  Typography,
  Button,
  Box,
  Container,
  IconButton,
  Drawer,
  List,
  ListItem,
  ListItemButton,
  ListItemText,
  useMediaQuery,
  useTheme,
} from '@mui/material';
import MenuIcon from '@mui/icons-material/Menu';
import CloseIcon from '@mui/icons-material/Close';
import { useNavigate } from 'react-router-dom';
import { APP_NAME, ROUTES } from '../constants';

const Navbar: React.FC = () => {
  const navigate = useNavigate();
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md')); // Below 768px
  const [mobileOpen, setMobileOpen] = useState(false);

  const handleDrawerToggle = () => {
    setMobileOpen(!mobileOpen);
  };

  const handleNavigation = (route: string) => {
    navigate(route);
    setMobileOpen(false);
  };

  const navigationItems = [
    { label: 'Home', route: ROUTES.HOME },
    { label: 'Login', route: ROUTES.LOGIN },
    { label: 'Register', route: ROUTES.REGISTER },
    { label: 'Dashboard', route: ROUTES.DASHBOARD },
  ];

  const drawer = (
    <Box sx={{ width: 250 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', p: 2 }}>
        <Typography variant="h6" sx={{ color: 'text.primary', fontWeight: 600 }}>
          {APP_NAME}
        </Typography>
        <IconButton onClick={handleDrawerToggle}>
          <CloseIcon />
        </IconButton>
      </Box>
      <List>
        {navigationItems.map((item) => (
          <ListItem key={item.label} disablePadding>
            <ListItemButton
              onClick={() => handleNavigation(item.route)}
              sx={{
                mx: 2,
                my: 0.5,
                borderRadius: '25px',
                backgroundColor: '#ffffff',
                '&:hover': {
                  backgroundColor: 'rgba(255, 255, 255, 0.8)',
                }
              }}
            >
              <ListItemText 
                primary={item.label} 
                sx={{ 
                  textAlign: 'center',
                  '& .MuiListItemText-primary': {
                    color: 'text.primary',
                    fontWeight: 500,
                  }
                }} 
              />
            </ListItemButton>
          </ListItem>
        ))}
      </List>
    </Box>
  );

  return (
    <>
      <AppBar 
        position="static"
        sx={{
          backgroundColor: 'rgba(0, 0, 0, 0.1)',
          backdropFilter: 'blur(20px)',
          boxShadow: 'none',
          borderBottom: '1px solid rgba(0, 0, 0, 0.1)',
        }}
      >
        <Container maxWidth="lg">
          <Toolbar>
            <Typography
              variant="h6"
              component="div"
              sx={{ 
                flexGrow: 1, 
                cursor: 'pointer',
                color: 'text.primary',
                fontWeight: 600,
              }}
              onClick={() => navigate(ROUTES.HOME)}
            >
              {APP_NAME}
            </Typography>
            
            {/* Desktop Navigation */}
            {!isMobile && (
              <Box sx={{ display: 'flex', gap: 2 }}>
                {navigationItems.map((item) => (
                  <Button 
                    key={item.label}
                    sx={{ 
                      color: 'text.primary',
                      fontWeight: 500,
                      backgroundColor: '#ffffff',
                      borderRadius: '50px',
                      px: 3,
                      py: 1,
                      '&:hover': {
                        backgroundColor: 'rgba(255, 255, 255, 0.8)',
                      }
                    }} 
                    onClick={() => navigate(item.route)}
                  >
                    {item.label}
                  </Button>
                ))}
              </Box>
            )}

            {/* Mobile Menu Button */}
            {isMobile && (
              <IconButton
                color="inherit"
                aria-label="open drawer"
                edge="end"
                onClick={handleDrawerToggle}
                sx={{ 
                  color: 'text.primary',
                  backgroundColor: '#ffffff',
                  borderRadius: '50px',
                  boxShadow: '0px 8px 32px rgba(0, 0, 0, 0.12)',
                  '&:hover': {
                    backgroundColor: 'rgba(255, 255, 255, 0.8)',
                  }
                }}
              >
                <MenuIcon />
              </IconButton>
            )}
          </Toolbar>
        </Container>
      </AppBar>

      {/* Mobile Drawer */}
      <Drawer
        variant="temporary"
        anchor="right"
        open={mobileOpen}
        onClose={handleDrawerToggle}
        ModalProps={{
          keepMounted: true, // Better open performance on mobile.
        }}
        sx={{
          '& .MuiDrawer-paper': {
            boxSizing: 'border-box',
            width: 250,
            backgroundColor: 'rgba(216 179 243 / 0.2)',
            backdropFilter: 'blur(20px)',
            borderLeft: '1px solid rgba(255, 255, 255, 0.3)',
          },
          '& .MuiBackdrop-root': {
            backgroundColor: 'transparent',
          },
        }}
      >
        {drawer}
      </Drawer>
    </>
  );
};

export default Navbar;
