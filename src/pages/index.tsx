import React, { JSX } from 'react';
import clsx from 'clsx';
import Link from '@docusaurus/Link';
import useDocusaurusContext from '@docusaurus/useDocusaurusContext';
import Layout from '@theme/Layout';
import Heading from '@theme/Heading';
import styles from './index.module.css';

interface FeatureCard {
  title: string;
  icon: string;
  description: string;
  link: string;
}

const features: FeatureCard[] = [
  {
    title: 'ROS 2 Fundamentals',
    icon: '🤖',
    description: 'Master the Robot Operating System 2, the industry standard for robotics development and communication.',
    link: '/02-ros2',
  },
  {
    title: 'Digital Twin Simulation',
    icon: '🌐',
    description: 'Create virtual replicas of physical robots using Gazebo, Unity, and advanced simulation environments.',
    link: '/03-digital-twin',
  },
  {
    title: 'NVIDIA Isaac Sim',
    icon: '⚡',
    description: 'Harness GPU-accelerated simulation and photorealistic rendering for advanced robotics training.',
    link: '/04-isaac-sim',
  },
  {
    title: 'Vision-Language-Action',
    icon: '👁️',
    description: 'Integrate AI vision models with language understanding to enable intelligent robotic decision-making.',
    link: '/05-vision-language-action',
  },
  {
    title: 'Humanoid Control',
    icon: '🦾',
    description: 'Learn inverse kinematics, gait generation, and reinforcement learning for bipedal robot control.',
    link: '/06-humanoid-control',
  },
  {
    title: 'Complete Projects',
    icon: '🚀',
    description: 'Build end-to-end robotics applications combining all modules into production-ready systems.',
    link: '/intro',
  },
];

function HeroSection() {
  const { siteConfig } = useDocusaurusContext();

  return (
    <header className={styles.hero}>
      <div className={styles.heroBackground}>
        <div className={styles.heroGrid}></div>
        <div className={styles.heroGradient}></div>
      </div>

      <div className={styles.heroContent}>
        <div className={styles.heroText}>
          <div className={styles.badge}>
            <span className={styles.badgeDot}></span>
            Next-Gen Robotics Education
          </div>

          <Heading as="h1" className={styles.heroTitle}>
            {siteConfig.title}
          </Heading>

          <p className={styles.heroSubtitle}>
            {siteConfig.tagline}
          </p>

          <p className={styles.heroDescription}>
            From ROS 2 basics to advanced humanoid control, master the complete stack
            of modern robotics development with hands-on projects and real-world applications.
          </p>

          <div className={styles.heroButtons}>
            <Link
              className={clsx('button button--lg', styles.btnPrimary)}
              to="/intro">
              Get Started
              <span className={styles.btnArrow}>→</span>
            </Link>

            <Link
              className={clsx('button button--lg', styles.btnSecondary)}
              href="https://github.com/facebook/docusaurus">
              <svg className={styles.githubIcon} viewBox="0 0 24 24" fill="currentColor">
                <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/>
              </svg>
              GitHub
            </Link>
          </div>
        </div>
      </div>
    </header>
  );
}

function FeatureCards() {
  return (
    <section className={styles.features}>
      <div className={styles.featuresContainer}>
        <div className={styles.featuresHeader}>
          <h2 className={styles.featuresTitle}>Course Modules</h2>
          <p className={styles.featuresSubtitle}>
            Comprehensive curriculum covering the entire robotics development pipeline
          </p>
        </div>

        <div className={styles.cardsGrid}>
          {features.map((feature, idx) => (
            <Link
              key={idx}
              to={feature.link}
              className={styles.card}>
              <div className={styles.cardGlow}></div>
              <div className={styles.cardContent}>
                <div className={styles.cardIcon}>{feature.icon}</div>
                <h3 className={styles.cardTitle}>{feature.title}</h3>
                <p className={styles.cardDescription}>{feature.description}</p>
                <div className={styles.cardArrow}>
                  <span>Explore</span>
                  <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                    <path d="M6 3L11 8L6 13" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                  </svg>
                </div>
              </div>
            </Link>
          ))}
        </div>
      </div>
    </section>
  );
}

export default function Home(): JSX.Element {
  const { siteConfig } = useDocusaurusContext();

  return (
    <Layout
      title={`Home`}
      description="Master Physical AI and Humanoid Robotics with comprehensive tutorials covering ROS 2, simulation, vision-language models, and advanced control systems.">
      <HeroSection />
      <main>
        <FeatureCards />
      </main>
    </Layout>
  );
}
